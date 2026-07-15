# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     rdavydov.py
   Description :   rdavydov/proxy-list 代理源 (http/socks4/socks5, actualizado c/ hora)
   Author :        Claude
   date：          2026/07/14
-------------------------------------------------
"""
__author__ = 'Claude'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class RdavydovFetcher(BaseFetcher):
    """rdavydov/proxy-list https://github.com/rdavydov/proxy-list"""

    name = "rdavydov"
    url = "https://github.com/rdavydov/proxy-list"

    enabled = True

    SOURCES = (
        "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/http.txt",
        "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks4.txt",
        "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks5.txt",
    )

    def fetch(self):
        proxies = []
        for source_url in self.SOURCES:
            try:
                r = WebRequest().get(source_url, timeout=10, retry_time=1)
                proxies.extend(self.parseProxiesFromText(r.text))
            except Exception as e:
                logger.error("ProxyFetch - rdavydov (%s): %s" % (source_url, e))
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in RdavydovFetcher().fetch():
        print(proxy)
