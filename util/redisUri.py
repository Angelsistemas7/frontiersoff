# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     redisUri
   Description :   Helper compartido para detectar si un DB_CONN pide TLS
                    (esquema "rediss://", el que exigen proveedores Redis
                    gratis como Upstash). Antes esto se hubiera duplicado en
                    db/dbClient.py, handler/controlHandler.py y
                    handler/sessionHandler.py por separado.
   Author :        Claude
   date：          2026/07/11
-------------------------------------------------
"""
__author__ = 'Claude'


def isTlsScheme(scheme):
    return (scheme or "").strip().lower() == "rediss"
