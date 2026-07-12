# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     prxchk.py
   Description :   prxchk/proxy-list 代理源
   Author :        Claude
   date：          2026/07/12
-------------------------------------------------
"""
__author__ = 'Claude'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class PrxchkFetcher(BaseFetcher):
    """prxchk/proxy-list https://github.com/prxchk/proxy-list"""

    name = "prxchk"
    url = "https://github.com/prxchk/proxy-list"

    enabled = True

    def fetch(self):
        proxies = []
        try:
            r = WebRequest().get(
                "https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt",
                timeout=10, retry_time=1)
            proxies.extend(self.parseProxiesFromText(r.text))
        except Exception as e:
            logger.error("ProxyFetch - prxchk: %s" % str(e))
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in PrxchkFetcher().fetch():
        print(proxy)
