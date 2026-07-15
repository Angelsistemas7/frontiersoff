# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     mrmarble.py
   Description :   MrMarble/proxy-list 代理源
   Author :        Claude
   date：          2026/07/14
-------------------------------------------------
"""
__author__ = 'Claude'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class MrMarbleFetcher(BaseFetcher):
    """MrMarble/proxy-list https://github.com/MrMarble/proxy-list"""

    name = "mrmarble"
    url = "https://github.com/MrMarble/proxy-list"

    enabled = True

    SOURCES = (
        "https://raw.githubusercontent.com/MrMarble/proxy-list/main/all.txt",
    )

    def fetch(self):
        proxies = []
        for source_url in self.SOURCES:
            try:
                r = WebRequest().get(source_url, timeout=10, retry_time=1)
                proxies.extend(self.parseProxiesFromText(r.text))
            except Exception as e:
                logger.error("ProxyFetch - mrmarble (%s): %s" % (source_url, e))
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in MrMarbleFetcher().fetch():
        print(proxy)
