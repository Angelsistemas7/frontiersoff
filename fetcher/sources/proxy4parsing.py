# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxy4parsing.py
   Description :   proxy4parsing/proxy-list 代理源 (solo HTTP, actualizado seguido)
   Author :        Claude
   date：          2026/07/14
-------------------------------------------------
"""
__author__ = 'Claude'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class Proxy4ParsingFetcher(BaseFetcher):
    """proxy4parsing/proxy-list https://github.com/proxy4parsing/proxy-list"""

    name = "proxy4parsing"
    url = "https://github.com/proxy4parsing/proxy-list"

    enabled = True

    SOURCES = (
        "https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http.txt",
    )

    def fetch(self):
        proxies = []
        for source_url in self.SOURCES:
            try:
                r = WebRequest().get(source_url, timeout=10, retry_time=1)
                proxies.extend(self.parseProxiesFromText(r.text))
            except Exception as e:
                logger.error("ProxyFetch - proxy4parsing (%s): %s" % (source_url, e))
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in Proxy4ParsingFetcher().fetch():
        print(proxy)
