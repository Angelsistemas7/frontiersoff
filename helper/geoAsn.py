# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     geoAsn
   Description :   Geolocalización + ASN de una IP (país, ciudad, ASN, ISP)
                    vía ip-api.com (gratis, sin API key, ~45 req/min) y una
                    clasificación heurística datacenter vs residencial/móvil
                    basada en el nombre del ISP/organización.
   Author :        Claude
   date：          2026/07/10
-------------------------------------------------
"""
import requests

from handler.logHandler import LogHandler

log = LogHandler("geo_asn")

GEO_API_URL = "http://ip-api.com/json/%s"
GEO_API_FIELDS = "status,message,country,countryCode,city,isp,org,as,query"

# Nombres/fragmentos comunes de proveedores de datacenter/hosting. No es
# exhaustivo ni 100% preciso (no hay una base de datos gratuita perfecta de
# tipo-de-ASN) pero da una señal util de "que tan humano" es el ISP.
DATACENTER_KEYWORDS = (
    "amazon", "aws", "google", "microsoft", "azure", "digitalocean",
    "ovh", "hetzner", "linode", "akamai", "cloudflare", "alibaba",
    "tencent", "vultr", "oracle", "scaleway", "contabo", "leaseweb",
    "choopa", "psychz", "hostinger", "hosting", "datacenter",
    "data center", "colocation", "cloud computing",
)


def classifyNetwork(isp, org):
    """ datacenter | residential_or_unknown """
    text = ("%s %s" % (isp or "", org or "")).lower()
    for kw in DATACENTER_KEYWORDS:
        if kw in text:
            return "datacenter"
    return "residential_or_unknown"


def lookup(ip):
    """
    Returns:
        dict {country, city, asn, isp, network_type} o {} si falla.
    """
    try:
        r = requests.get(GEO_API_URL % ip, params={"fields": GEO_API_FIELDS}, timeout=4)
        data = r.json()
        if data.get("status") != "success":
            return {}
        as_field = data.get("as") or ""  # ej: "AS15169 Google LLC"
        asn = as_field.split(" ", 1)[0] if as_field else ""
        isp = data.get("isp", "")
        org = data.get("org", "")
        return {
            "country": data.get("countryCode", ""),
            "city": data.get("city", ""),
            "asn": asn,
            "isp": isp,
            "network_type": classifyNetwork(isp, org),
        }
    except Exception as e:
        log.error("geoAsn lookup failed for %s: %s" % (ip, str(e)))
        return {}
