# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     hookzof.py
   Description :   hookzof/socks5_list 代理源 (SOCKS5, lista grande
                    actualizada por CI cada 30 min).
   Author :        Claude
   date：          2026/07/12
-------------------------------------------------
"""
__author__ = 'Claude'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class HookzofFetcher(BaseFetcher):
    """hookzof/socks5_list https://github.com/hookzof/socks5_list"""

    name = "hookzof"
    url = "https://github.com/hookzof/socks5_list"

    enabled = True

    SOURCES = (
        "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
    )

    def fetch(self):
        proxies = []
        for source_url in self.SOURCES:
            try:
                r = WebRequest().get(source_url, timeout=10, retry_time=1)
                proxies.extend(self.parseProxiesFromText(r.text))
            except Exception as e:
                logger.error("ProxyFetch - hookzof (%s): %s" % (source_url, e))
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in HookzofFetcher().fetch():
        print(proxy)
