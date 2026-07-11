# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     protocolChecker
   Description :   Detecta si un proxy (ademas de HTTP/HTTPS, ya cubierto
                    por validator.py) tambien responde como SOCKS5. No es
                    un requisito para que el proxy sea usable - es una
                    capacidad adicional que habilita resolucion de DNS del
                    lado del proxy (mas privacidad) cuando el cliente se
                    conecta con socks5h:// en vez de socks5://.
   Author :        Claude
   date：          2026/07/11
-------------------------------------------------
"""
import socket

import requests

from handler.configHandler import ConfigHandler

conf = ConfigHandler()


def checkSocks5(proxy_str, timeout=None):
    """ True si el proxy responde correctamente como SOCKS5 (con DNS remoto) """
    timeout = timeout or conf.verifyTimeout
    proxies = {"http": "socks5h://%s" % proxy_str, "https": "socks5h://%s" % proxy_str}
    try:
        r = requests.head(conf.httpUrl, proxies=proxies, timeout=timeout)
        return r.status_code == 200
    except Exception:
        return False


def checkSshBanner(host, port=22, timeout=3):
    """
    True si el host responde con un banner SSH ("SSH-...") en el puerto dado.

    Nota: esto es solo informativo. Un proxy publico scrapeado que ademas
    tenga SSH abierto no sirve como tunel sin credenciales (SSH siempre
    requiere autenticacion, a diferencia de un proxy HTTP/SOCKS5 abierto) -
    en la practica casi siempre da False para proxies random. Es realmente
    util para tus propios nodos (un VPS tuyo con SSH real, donde podrias
    hacer `ssh -D <puerto> usuario@host` para armar un tunel SOCKS5 local).
    """
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            banner = sock.recv(64)
            return banner.startswith(b"SSH-")
    except Exception:
        return False
