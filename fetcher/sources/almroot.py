# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     almroot.py
   Description :   almroot/proxylist 代理源
   Author :        Claude
   date：          2026/07/14
-------------------------------------------------
"""
__author__ = 'Claude'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class AlmrootFetcher(BaseFetcher):
    """almroot/proxylist https://github.com/almroot/proxylist"""

    name = "almroot"
    url = "https://github.com/almroot/proxylist"

    enabled = True

    SOURCES = (
        "https://raw.githubusercontent.com/almroot/proxylist/master/list.txt",
    )

    def fetch(self):
        proxies = []
        for source_url in self.SOURCES:
            try:
                r = WebRequest().get(source_url, timeout=10, retry_time=1)
                proxies.extend(self.parseProxiesFromText(r.text))
            except Exception as e:
                logger.error("ProxyFetch - almroot (%s): %s" % (source_url, e))
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in AlmrootFetcher().fetch():
        print(proxy)
