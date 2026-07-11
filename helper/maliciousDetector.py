# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     maliciousDetector
   Description :   Detecta manipulacion de trafico por parte de un proxy
                    (inyeccion de contenido, MITM de TLS, headers añadidos,
                    redirecciones sospechosas) y produce un puntaje de riesgo
                    0-100 con el detalle de cada señal encontrada.
   Author :        Claude
   date：          2026/07/10
-------------------------------------------------
"""
import difflib
import hashlib
import socket
import ssl
import threading
import time
from urllib.parse import urlparse

import requests

from handler.configHandler import ConfigHandler
from handler.logHandler import LogHandler
from helper import netutil

conf = ConfigHandler()
log = LogHandler("malicious_detector")

# Headers que un proxy honesto agrega habitualmente; cualquier otro header
# nuevo en la respuesta-eco se considera una señal (no necesariamente
# maliciosa por si sola, pero sospechosa).
EXPECTED_PROXY_HEADERS = {
    "via", "x-forwarded-for", "x-forwarded-proto", "x-forwarded-port",
    "x-real-ip", "forwarded", "x-cache", "x-cache-lookup", "connection",
    "accept-encoding", "host", "x-amzn-trace-id",
}

INJECTION_MARKERS = ("<script", "<iframe", "document.write")

_baseline_lock = threading.Lock()
_baseline = None
_baseline_ts = 0
_BASELINE_TTL = 1800  # 30 min


def _proxies_dict(proxy_str):
    return {"http": "http://%s" % proxy_str, "https": "http://%s" % proxy_str}


def _split_proxy(proxy_str):
    """ soporta 'ip:port', 'user:pass@ip:port' y sus variantes IPv6 """
    return netutil.splitHostPort(netutil.stripAuth(proxy_str))


def _fetch_baseline():
    """ Contenido/headers/certificado obtenidos SIN proxy, usados como referencia """
    baseline = {"content_body": "", "tls_fingerprint": ""}
    try:
        r = requests.get(conf.maliciousCanaryHttpUrl, timeout=8)
        baseline["content_body"] = r.text
    except Exception as e:
        log.error("baseline content fetch failed: %s" % str(e))
    try:
        baseline["tls_fingerprint"] = _cert_fingerprint_direct(
            urlparse(conf.maliciousCanaryHttpsUrl).hostname)
    except Exception as e:
        log.error("baseline tls fetch failed: %s" % str(e))
    return baseline


def _get_baseline():
    global _baseline, _baseline_ts
    with _baseline_lock:
        if _baseline is None or (time.time() - _baseline_ts) > _BASELINE_TTL:
            _baseline = _fetch_baseline()
            _baseline_ts = time.time()
        return _baseline


def _cert_fingerprint_direct(host, port=443, timeout=8):
    ctx = ssl.create_default_context()
    with socket.create_connection((host, port), timeout=timeout) as sock:
        with ctx.wrap_socket(sock, server_hostname=host) as tls_sock:
            der = tls_sock.getpeercert(binary_form=True)
    return hashlib.sha256(der).hexdigest()


def _cert_fingerprint_via_proxy(proxy_str, host, port=443, timeout=8):
    proxy_host, proxy_port = _split_proxy(proxy_str)
    with socket.create_connection((proxy_host, proxy_port), timeout=timeout) as sock:
        sock.sendall(("CONNECT %s:%s HTTP/1.1\r\nHost: %s:%s\r\n\r\n" %
                       (host, port, host, port)).encode())
        resp = sock.recv(4096)
        if b" 200 " not in resp.split(b"\r\n", 1)[0] and not resp.split(b"\r\n", 1)[0].endswith(b"200 Connection established"):
            raise ConnectionError("CONNECT tunnel rejected: %r" % resp[:80])
        ctx = ssl.create_default_context()
        # No validamos la cadena de confianza: justamente queremos poder
        # inspeccionar un certificado auto-firmado/MITM sin que falle antes.
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with ctx.wrap_socket(sock, server_hostname=host) as tls_sock:
            der = tls_sock.getpeercert(binary_form=True)
    return hashlib.sha256(der).hexdigest()


def inspect(proxy_str):
    """
    Ejecuta todas las señales de manipulación contra un proxy.
    Returns:
        (risk_score:int 0-100, reasons:list[dict{check,points,detail}])
    """
    baseline = _get_baseline()
    reasons = []

    # 1) Certificado TLS distinto -> el proxy está interceptando HTTPS (MITM)
    if baseline.get("tls_fingerprint"):
        try:
            host = urlparse(conf.maliciousCanaryHttpsUrl).hostname
            fp = _cert_fingerprint_via_proxy(proxy_str, host)
            if fp != baseline["tls_fingerprint"]:
                reasons.append({
                    "check": "tls_fingerprint_mismatch",
                    "points": 60,
                    "detail": ("El certificado TLS de %s visto a través del proxy no coincide "
                               "con el original: el proxy está interceptando tráfico HTTPS cifrado "
                               "(posible ataque MITM).") % host,
                })
        except Exception:
            pass  # inconcluso (p.ej. el proxy no soporta CONNECT a 443): no penaliza

    # 2) Contenido de una página estática conocida, alterado o con inyección
    try:
        r = requests.get(conf.maliciousCanaryHttpUrl, proxies=_proxies_dict(proxy_str),
                          timeout=8, allow_redirects=True)
        body_lower = r.text.lower()
        baseline_lower = baseline.get("content_body", "").lower()
        injected = [m for m in INJECTION_MARKERS if m in body_lower and m not in baseline_lower]
        similarity = (difflib.SequenceMatcher(None, baseline["content_body"], r.text).ratio()
                      if baseline.get("content_body") else 1.0)
        if injected and similarity < 0.3:
            # No es una inyección puntual: la página completa fue reemplazada por
            # otro contenido (visto en producción: un proxy devolvía una web de
            # inversiones en chino en vez de la página pedida). Mucho más grave
            # que agregar un script/ad a una página que sigue siendo la original.
            reasons.append({
                "check": "content_hijack",
                "points": 70,
                "detail": ("El proxy reemplazó la página completa por otro contenido no relacionado "
                           "(incluye %s, similitud %.0f%% con el original) — no es una simple "
                           "inyección, devuelve una página distinta a la solicitada.") % (
                    ", ".join(injected), similarity * 100),
            })
        elif injected:
            reasons.append({
                "check": "content_injection",
                "points": 50,
                "detail": ("El proxy inyectó contenido (%s) en una página que normalmente "
                           "no lo tiene.") % ", ".join(injected),
            })
        elif baseline.get("content_body") and similarity < 0.9:
            reasons.append({
                "check": "content_modified",
                "points": 25,
                "detail": "El contenido de la página de referencia fue alterado (similitud %.0f%%)." % (
                    similarity * 100),
            })

        # 2b) redirección a un dominio distinto al solicitado
        if r.history:
            final_host = urlparse(r.url).hostname
            expected_host = urlparse(conf.maliciousCanaryHttpUrl).hostname
            if final_host and final_host != expected_host:
                reasons.append({
                    "check": "suspicious_redirect",
                    "points": 40,
                    "detail": "El proxy redirigió la petición hacia %s en vez de %s." % (
                        final_host, expected_host),
                })
    except Exception:
        pass

    # 3) Headers añadidos que el servidor recibió pero que nosotros no enviamos
    try:
        sent_headers = {"User-Agent": "proxy-manager-canary/1.0", "Accept": "*/*"}
        r2 = requests.get(conf.maliciousCanaryEchoUrl, headers=sent_headers,
                           proxies=_proxies_dict(proxy_str), timeout=8)
        seen_headers = {k.lower(): v for k, v in r2.json().get("headers", {}).items()}
        sent_lower = {k.lower() for k in sent_headers}
        extra = {k: v for k, v in seen_headers.items()
                 if k not in sent_lower and k not in EXPECTED_PROXY_HEADERS}
        if extra:
            reasons.append({
                "check": "header_injection",
                "points": min(15 * len(extra), 45),
                "detail": "El proxy agregó headers no solicitados: %s." % (
                    ", ".join("%s=%s" % (k, v) for k, v in extra.items())),
            })
    except Exception:
        pass

    risk_score = min(sum(r["points"] for r in reasons), 100)
    return risk_score, reasons
