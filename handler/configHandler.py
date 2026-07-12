# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     configHandler
   Description :
   Author :        JHao
   date：          2020/6/22
-------------------------------------------------
   Change Activity:
                   2020/6/22:
-------------------------------------------------
"""
__author__ = 'JHao'

import os
import setting
from util.singleton import Singleton
from util.lazyProperty import LazyProperty
from util.six import reload_six, withMetaclass

_control_handler = None


class ConfigHandler(withMetaclass(Singleton)):

    def __init__(self):
        pass

    @LazyProperty
    def serverHost(self):
        return os.environ.get("HOST", setting.HOST)

    @LazyProperty
    def serverPort(self):
        return os.environ.get("PORT", setting.PORT)

    @LazyProperty
    def apiKey(self):
        # solo por variable de entorno, igual que abuseIpdbApiKey: nunca en
        # setting.py ni editable via dashboard, para no exponerla.
        return os.getenv("API_KEY", setting.API_KEY)

    @LazyProperty
    def dbConn(self):
        return os.getenv("DB_CONN", setting.DB_CONN)

    @LazyProperty
    def tableName(self):
        return os.getenv("TABLE_NAME", setting.TABLE_NAME)

    @property
    def fetcherExclude(self):
        env = os.getenv("PROXY_FETCHER_EXCLUDE")
        if env is not None:
            return [name.strip() for name in env.split(",") if name.strip()]
        reload_six(setting)
        return getattr(setting, 'PROXY_FETCHER_EXCLUDE', [])

    @LazyProperty
    def fetchThreadJoinTimeout(self):
        return int(os.getenv("FETCH_THREAD_JOIN_TIMEOUT", setting.FETCH_THREAD_JOIN_TIMEOUT))

    @LazyProperty
    def httpUrl(self):
        return os.getenv("HTTP_URL", setting.HTTP_URL)

    @LazyProperty
    def httpsUrl(self):
        return os.getenv("HTTPS_URL", setting.HTTPS_URL)

    @property
    def verifyTimeout(self):
        return self._editable("VERIFY_TIMEOUT", "verifyTimeout")

    # @LazyProperty
    # def proxyCheckCount(self):
    #     return int(os.getenv("PROXY_CHECK_COUNT", setting.PROXY_CHECK_COUNT))

    @property
    def maxFailCount(self):
        return self._editable("MAX_FAIL_COUNT", "maxFailCount")

    # @LazyProperty
    # def maxFailRate(self):
    #     return int(os.getenv("MAX_FAIL_RATE", setting.MAX_FAIL_RATE))

    @property
    def poolSizeMin(self):
        return self._editable("POOL_SIZE_MIN", "poolSizeMin")

    @LazyProperty
    def proxyRegion(self):
        return bool(os.getenv("PROXY_REGION", setting.PROXY_REGION))

    @LazyProperty
    def timezone(self):
        return os.getenv("TIMEZONE", setting.TIMEZONE)

    @LazyProperty
    def maliciousCanaryHttpUrls(self):
        env = os.getenv("MALICIOUS_CANARY_HTTP_URLS")
        return env.split(",") if env else setting.MALICIOUS_CANARY_HTTP_URLS

    @LazyProperty
    def maliciousCanaryHttpsUrls(self):
        env = os.getenv("MALICIOUS_CANARY_HTTPS_URLS")
        return env.split(",") if env else setting.MALICIOUS_CANARY_HTTPS_URLS

    @LazyProperty
    def maliciousCanaryEchoUrls(self):
        env = os.getenv("MALICIOUS_CANARY_ECHO_URLS")
        return env.split(",") if env else setting.MALICIOUS_CANARY_ECHO_URLS

    @property
    def maliciousQuarantineThreshold(self):
        return self._editable("MALICIOUS_QUARANTINE_THRESHOLD", "maliciousQuarantineThreshold")

    @property
    def maliciousConfirmThreshold(self):
        return self._editable("MALICIOUS_CONFIRM_THRESHOLD", "maliciousConfirmThreshold")

    @property
    def maliciousConfirmStrikes(self):
        return self._editable("MALICIOUS_CONFIRM_STRIKES", "maliciousConfirmStrikes")

    @LazyProperty
    def abuseIpdbApiKey(self):
        # solo por variable de entorno: nunca vía dashboard/Redis para no
        # exponer la key en un endpoint de config legible.
        return os.getenv("ABUSEIPDB_API_KEY", setting.ABUSEIPDB_API_KEY)

    @LazyProperty
    def abuseIpdbEnabled(self):
        env = os.getenv("ABUSEIPDB_ENABLED")
        if env is not None:
            return env.lower() not in ("0", "false", "")
        return bool(setting.ABUSEIPDB_ENABLED)

    @LazyProperty
    def abuseIpdbCategories(self):
        return os.getenv("ABUSEIPDB_CATEGORIES", setting.ABUSEIPDB_CATEGORIES)

    @property
    def whitelistMinChecks(self):
        return self._editable("WHITELIST_MIN_CHECKS", "whitelistMinChecks")

    @property
    def whitelistMaxLatencyMs(self):
        return self._editable("WHITELIST_MAX_LATENCY_MS", "whitelistMaxLatencyMs")

    @property
    def viewerSafeMinChecks(self):
        return self._editable("VIEWER_SAFE_MIN_CHECKS", "viewerSafeMinChecks")

    @property
    def viewerSafeMinBandwidthKbps(self):
        return self._editable("VIEWER_SAFE_MIN_BANDWIDTH_KBPS", "viewerSafeMinBandwidthKbps")

    @property
    def stickyDefaultTtl(self):
        return self._editable("STICKY_DEFAULT_TTL", "stickyDefaultTtl")

    @property
    def stickyMaxTtl(self):
        return self._editable("STICKY_MAX_TTL", "stickyMaxTtl")

    @LazyProperty
    def bandwidthTestUrl(self):
        return os.getenv("BANDWIDTH_TEST_URL", setting.BANDWIDTH_TEST_URL)

    @LazyProperty
    def bandwidthTestSizeBytes(self):
        return int(os.getenv("BANDWIDTH_TEST_SIZE_BYTES", setting.BANDWIDTH_TEST_SIZE_BYTES))

    @LazyProperty
    def bandwidthTestTimeout(self):
        return int(os.getenv("BANDWIDTH_TEST_TIMEOUT", setting.BANDWIDTH_TEST_TIMEOUT))

    def _editable(self, env_var, control_key):
        """
        Valor editable en caliente desde el dashboard (Redis, via ControlHandler),
        con la variable de entorno como override explícito de mayor prioridad
        (para despliegues), y el default de setting.py como último fallback.
        """
        env = os.getenv(env_var)
        if env is not None:
            return int(env)
        return self._controlHandler().get_value(control_key)

    def _controlHandler(self):
        global _control_handler
        if _control_handler is None:
            from handler.controlHandler import ControlHandler
            _control_handler = ControlHandler()
        return _control_handler

