# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     vakhov.py
   Description :   vakhov/fresh-proxy-list 代理源
   Author :        Claude
   date：          2026/07/12
-------------------------------------------------
"""
__author__ = 'Claude'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class VakhovFetcher(BaseFetcher):
    """vakhov/fresh-proxy-list https://github.com/vakhov/fresh-proxy-list"""

    name = "vakhov"
    url = "https://github.com/vakhov/fresh-proxy-list"

    enabled = True

    def fetch(self):
        proxies = []
        try:
            r = WebRequest().get(
                "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/proxylist.txt",
                timeout=10, retry_time=1)
            proxies.extend(self.parseProxiesFromText(r.text))
        except Exception as e:
            logger.error("ProxyFetch - vakhov: %s" % str(e))
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in VakhovFetcher().fetch():
        print(proxy)
