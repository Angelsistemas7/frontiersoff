# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     b4rc0detm.py
   Description :   B4RC0DE-TM/proxy-list 代理源 (volumen alto)
   Author :        Claude
   date：          2026/07/14
-------------------------------------------------
"""
__author__ = 'Claude'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class B4rc0deTmFetcher(BaseFetcher):
    """B4RC0DE-TM/proxy-list https://github.com/B4RC0DE-TM/proxy-list"""

    name = "b4rc0detm"
    url = "https://github.com/B4RC0DE-TM/proxy-list"

    enabled = True

    SOURCES = (
        "https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/HTTP.txt",
    )

    def fetch(self):
        proxies = []
        for source_url in self.SOURCES:
            try:
                r = WebRequest().get(source_url, timeout=10, retry_time=1)
                proxies.extend(self.parseProxiesFromText(r.text))
            except Exception as e:
                logger.error("ProxyFetch - b4rc0detm (%s): %s" % (source_url, e))
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in B4rc0deTmFetcher().fetch():
        print(proxy)
