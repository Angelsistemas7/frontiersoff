# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     abuseReporter
   Description :   Reporta proxies maliciosos confirmados a AbuseIPDB
                    (https://www.abuseipdb.com/api) para que otros usuarios
                    no caigan en ellos. Sin ABUSEIPDB_API_KEY configurada,
                    el reporte se omite silenciosamente.
   Author :        Claude
   date：          2026/07/10
-------------------------------------------------
"""
import requests

from handler.logHandler import LogHandler
from handler.configHandler import ConfigHandler
from helper import netutil

conf = ConfigHandler()
log = LogHandler("abuse_reporter")

REPORT_URL = "https://api.abuseipdb.com/api/v2/report"
COMMENT_MAX_LEN = 1024


def _extract_ip(proxy_str):
    """ soporta 'ip:port', 'user:pass@ip:port' y sus variantes IPv6 """
    return netutil.extractHost(proxy_str)


def _build_comment(proxy):
    details = "; ".join(r["detail"] for r in proxy.risk_reasons) or "manipulacion de trafico detectada"
    comment = "proxy-manager: %s (risk_score=%d)" % (details, proxy.risk_score)
    return comment[:COMMENT_MAX_LEN]


def report(proxy):
    """
    Reporta un proxy confirmado como malicioso a AbuseIPDB.
    Returns:
        True si se envio el reporte, False si se omitio o fallo.
    """
    if not conf.abuseIpdbEnabled:
        return False
    api_key = conf.abuseIpdbApiKey
    if not api_key:
        log.info("ABUSEIPDB_API_KEY no configurada, se omite el reporte de %s" % proxy.proxy)
        return False

    ip = _extract_ip(proxy.proxy)
    try:
        resp = requests.post(
            REPORT_URL,
            headers={"Key": api_key, "Accept": "application/json"},
            data={
                "ip": ip,
                "categories": conf.abuseIpdbCategories,
                "comment": _build_comment(proxy),
            },
            timeout=10,
        )
        if resp.status_code == 200:
            log.info("AbuseIPDB: reportado %s (score=%d)" % (ip, proxy.risk_score))
            return True
        log.error("AbuseIPDB respondio %s para %s: %s" % (resp.status_code, ip, resp.text[:200]))
        return False
    except Exception as e:
        log.error("AbuseIPDB: error reportando %s: %s" % (ip, str(e)))
        return False
