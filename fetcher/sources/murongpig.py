# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     murongpig.py
   Description :   MuRongPIG/Proxy-Master 代理源 (listas grandes, ~1.8MB c/u)
   Author :        Claude
   date：          2026/07/12
-------------------------------------------------
"""
__author__ = 'Claude'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class MuRongPIGFetcher(BaseFetcher):
    """MuRongPIG/Proxy-Master https://github.com/MuRongPIG/Proxy-Master"""

    name = "murongpig"
    url = "https://github.com/MuRongPIG/Proxy-Master"

    enabled = True

    SOURCES = (
        "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt",
        "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/socks5.txt",
    )

    def fetch(self):
        proxies = []
        for source_url in self.SOURCES:
            try:
                # listas grandes (~1.8MB) -> timeout mas generoso que el default
                r = WebRequest().get(source_url, timeout=20, retry_time=1)
                proxies.extend(self.parseProxiesFromText(r.text))
            except Exception as e:
                logger.error("ProxyFetch - murongpig (%s): %s" % (source_url, e))
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in MuRongPIGFetcher().fetch():
        print(proxy)
