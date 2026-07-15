# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     tuanminpay.py
   Description :   TuanMinPay/live-proxy 代理源 (http, actualizado seguido)
   Author :        Claude
   date：          2026/07/14
-------------------------------------------------
"""
__author__ = 'Claude'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class TuanMinPayFetcher(BaseFetcher):
    """TuanMinPay/live-proxy https://github.com/TuanMinPay/live-proxy"""

    name = "tuanminpay"
    url = "https://github.com/TuanMinPay/live-proxy"

    enabled = True

    SOURCES = (
        "https://raw.githubusercontent.com/TuanMinPay/live-proxy/master/http.txt",
    )

    def fetch(self):
        proxies = []
        for source_url in self.SOURCES:
            try:
                r = WebRequest().get(source_url, timeout=10, retry_time=1)
                proxies.extend(self.parseProxiesFromText(r.text))
            except Exception as e:
                logger.error("ProxyFetch - tuanminpay (%s): %s" % (source_url, e))
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in TuanMinPayFetcher().fetch():
        print(proxy)
