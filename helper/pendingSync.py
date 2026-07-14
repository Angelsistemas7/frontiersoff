# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     pendingSync
   Description :   Red de seguridad para cuando Redis (Upstash) no esta
                    disponible (ej. cuota mensual agotada): en vez de perder
                    los candidatos scrapeados esa corrida, se guardan como
                    archivos JSON en pending_sync/ (el workflow los
                    commitea al repo). La proxima corrida donde Redis SI
                    responda los recupera automaticamente y los borra.
   Author :        Claude
   date：          2026/07/14
-------------------------------------------------
"""
__author__ = 'Claude'

import json
import os
import time
import uuid

PENDING_DIR = "pending_sync"


def dump(candidate_strs, note=""):
    """ Guarda una lista de proxy str (ip:port) en un archivo nuevo de
    pending_sync/. No pisa nada - cada corrida que cae en este modo agrega
    su propio archivo con timestamp + sufijo random, para no perder
    corridas previas que todavia no se hayan podido consumir. El sufijo es
    necesario: hasta 40 shards de MuRongPIG pueden caer en este modo al
    mismo tiempo, y con solo timestamp de segundo dos corridas simultaneas
    se pisarian el archivo entre si (bug real encontrado al probar esto). """
    if not candidate_strs:
        return None
    os.makedirs(PENDING_DIR, exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    path = os.path.join(PENDING_DIR, "%s-%s.json" % (ts, uuid.uuid4().hex[:8]))
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"ts": ts, "note": note, "count": len(candidate_strs),
                    "candidates": candidate_strs}, f)
    return path


def loadAll():
    """ Lee y combina (deduplicado) todos los candidatos guardados en
    pending_sync/ de corridas anteriores. No borra nada - eso es trabajo
    de clearAll(), llamado solo despues de procesarlos con exito. """
    if not os.path.isdir(PENDING_DIR):
        return []
    seen = set()
    combined = []
    for name in sorted(os.listdir(PENDING_DIR)):
        if not name.endswith(".json"):
            continue
        with open(os.path.join(PENDING_DIR, name), encoding="utf-8") as f:
            data = json.load(f)
        for proxy_str in data.get("candidates", []):
            if proxy_str not in seen:
                seen.add(proxy_str)
                combined.append(proxy_str)
    return combined


def clearAll():
    """ Borra todos los archivos de pending_sync/ - llamar SOLO despues de
    que sus candidatos ya se hayan filtrado/validado con Redis disponible. """
    if not os.path.isdir(PENDING_DIR):
        return
    for name in os.listdir(PENDING_DIR):
        if name.endswith(".json"):
            os.remove(os.path.join(PENDING_DIR, name))
