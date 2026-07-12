# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     shiftytr.py
   Description :   ShiftyTR/Proxy-List 代理源
   Author :        Claude
   date：          2026/07/12
-------------------------------------------------
"""
__author__ = 'Claude'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class ShiftyTRFetcher(BaseFetcher):
    """ShiftyTR/Proxy-List https://github.com/ShiftyTR/Proxy-List"""

    name = "shiftytr"
    url = "https://github.com/ShiftyTR/Proxy-List"

    enabled = True

    SOURCES = (
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt",
    )

    def fetch(self):
        proxies = []
        for source_url in self.SOURCES:
            try:
                r = WebRequest().get(source_url, timeout=10, retry_time=1)
                proxies.extend(self.parseProxiesFromText(r.text))
            except Exception as e:
                logger.error("ProxyFetch - shiftytr (%s): %s" % (source_url, e))
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in ShiftyTRFetcher().fetch():
        print(proxy)
