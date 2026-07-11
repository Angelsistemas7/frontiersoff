# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     monosans.py
   Description :   monosans/proxy-list 代理源 (cobertura global, bien mantenido)
   Author :        Claude
   date：          2026/07/11
-------------------------------------------------
"""
__author__ = 'Claude'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class MonosansFetcher(BaseFetcher):
    """monosans/proxy-list https://github.com/monosans/proxy-list"""

    name = "monosans"
    url = "https://github.com/monosans/proxy-list"

    enabled = True

    SOURCES = (
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
    )

    def fetch(self):
        proxies = []
        for source_url in self.SOURCES:
            try:
                r = WebRequest().get(source_url, timeout=10, retry_time=1)
                proxies.extend(self.parseProxiesFromText(r.text))
            except Exception as e:
                logger.error("ProxyFetch - monosans (%s): %s" % (source_url, e))
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in MonosansFetcher().fetch():
        print(proxy)
