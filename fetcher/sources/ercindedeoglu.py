# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ercindedeoglu.py
   Description :   ErcinDedeoglu/proxies 代理源 (http/socks4/socks5, volumen alto)
   Author :        Claude
   date：          2026/07/14
-------------------------------------------------
"""
__author__ = 'Claude'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class ErcinDedeogluFetcher(BaseFetcher):
    """ErcinDedeoglu/proxies https://github.com/ErcinDedeoglu/proxies"""

    name = "ercindedeoglu"
    url = "https://github.com/ErcinDedeoglu/proxies"

    enabled = True

    SOURCES = (
        "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/http.txt",
        "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks4.txt",
        "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks5.txt",
    )

    def fetch(self):
        proxies = []
        for source_url in self.SOURCES:
            try:
                r = WebRequest().get(source_url, timeout=10, retry_time=1)
                proxies.extend(self.parseProxiesFromText(r.text))
            except Exception as e:
                logger.error("ProxyFetch - ercindedeoglu (%s): %s" % (source_url, e))
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in ErcinDedeogluFetcher().fetch():
        print(proxy)
