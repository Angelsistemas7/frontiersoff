# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     controlHandler
   Description :   Estado de control en caliente (pausa/reanudar, parametros
                    editables del detector) compartido entre el proceso
                    scheduler y el proceso server via Redis. No usa el
                    DbClient singleton para no interferir con la tabla del
                    pool principal.
   Author :        Claude
   date：          2026/07/10
-------------------------------------------------
"""
import os
import time
from urllib.parse import urlparse

import redis

import setting
from util.redisUri import isTlsScheme

CONTROL_KEY = "proxy_manager:control"
CONFIG_KEY = "proxy_manager:runtime_config"

# parametros que el dashboard puede editar en caliente, con su default de setting.py
EDITABLE_DEFAULTS = {
    "maliciousQuarantineThreshold": setting.MALICIOUS_QUARANTINE_THRESHOLD,
    "maliciousConfirmThreshold": setting.MALICIOUS_CONFIRM_THRESHOLD,
    "maliciousConfirmStrikes": setting.MALICIOUS_CONFIRM_STRIKES,
    "poolSizeMin": setting.POOL_SIZE_MIN,
    "verifyTimeout": setting.VERIFY_TIMEOUT,
    "maxFailCount": setting.MAX_FAIL_COUNT,
    "whitelistMinChecks": setting.WHITELIST_MIN_CHECKS,
    "whitelistMaxLatencyMs": setting.WHITELIST_MAX_LATENCY_MS,
    "stickyDefaultTtl": setting.STICKY_DEFAULT_TTL,
    "stickyMaxTtl": setting.STICKY_MAX_TTL,
}


def _db_conn():
    return os.getenv("DB_CONN", setting.DB_CONN)


class ControlHandler(object):
    """ Estado de pausa/reanudado + parametros editables en caliente """

    def __init__(self):
        conf = urlparse(_db_conn())
        self._redis = redis.Redis(host=conf.hostname, port=conf.port,
                                   password=conf.password, db=conf.path[1:] or 0,
                                   decode_responses=True, socket_timeout=5,
                                   socket_connect_timeout=5,
                                   ssl=isTlsScheme(conf.scheme))

    # ---------------- pausa / reanudado ----------------
    def is_paused(self):
        try:
            return self._redis.hget(CONTROL_KEY, "paused") == "1"
        except redis.RedisError:
            return False  # si Redis no responde, no bloqueamos el ciclo

    def pause(self):
        self._redis.hset(CONTROL_KEY, "paused", "1")

    def resume(self):
        self._redis.hset(CONTROL_KEY, "paused", "0")

    def mark_fetch(self):
        self._redis.hset(CONTROL_KEY, "last_fetch_at", str(int(time.time())))

    def mark_check(self):
        self._redis.hset(CONTROL_KEY, "last_check_at", str(int(time.time())))

    def status(self):
        try:
            data = self._redis.hgetall(CONTROL_KEY)
        except redis.RedisError:
            data = {}
        return {
            "paused": data.get("paused", "0") == "1",
            "last_fetch_at": int(data["last_fetch_at"]) if data.get("last_fetch_at") else None,
            "last_check_at": int(data["last_check_at"]) if data.get("last_check_at") else None,
        }

    # ---------------- parametros editables en caliente ----------------
    def get_config(self):
        try:
            stored = self._redis.hgetall(CONFIG_KEY)
        except redis.RedisError:
            stored = {}
        return {k: int(stored[k]) if k in stored else default
                for k, default in EDITABLE_DEFAULTS.items()}

    def get_value(self, key):
        try:
            v = self._redis.hget(CONFIG_KEY, key)
        except redis.RedisError:
            v = None
        return int(v) if v is not None else EDITABLE_DEFAULTS[key]

    def update_config(self, updates):
        clean = {}
        for key in EDITABLE_DEFAULTS:
            if key in updates and str(updates[key]).strip() != "":
                clean[key] = int(updates[key])
        if clean:
            self._redis.hset(CONFIG_KEY, mapping={k: str(v) for k, v in clean.items()})
        return self.get_config()
