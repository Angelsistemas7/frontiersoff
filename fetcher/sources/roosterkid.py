# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     roosterkid.py
   Description :   roosterkid/openproxylist 代理源
   Author :        Claude
   date：          2026/07/12
-------------------------------------------------
"""
__author__ = 'Claude'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class RoosterkidFetcher(BaseFetcher):
    """roosterkid/openproxylist https://github.com/roosterkid/openproxylist"""

    name = "roosterkid"
    url = "https://github.com/roosterkid/openproxylist"

    enabled = True

    SOURCES = (
        "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
        "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt",
    )

    def fetch(self):
        proxies = []
        for source_url in self.SOURCES:
            try:
                r = WebRequest().get(source_url, timeout=10, retry_time=1)
                proxies.extend(self.parseProxiesFromText(r.text))
            except Exception as e:
                logger.error("ProxyFetch - roosterkid (%s): %s" % (source_url, e))
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in RoosterkidFetcher().fetch():
        print(proxy)
