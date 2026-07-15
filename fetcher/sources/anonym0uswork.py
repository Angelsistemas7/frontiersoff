# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     anonym0uswork.py
   Description :   Anonym0usWork1221/Free-Proxies 代理源 (http/socks4/socks5)
   Author :        Claude
   date：          2026/07/14
-------------------------------------------------
"""
__author__ = 'Claude'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class Anonym0usWorkFetcher(BaseFetcher):
    """Anonym0usWork1221/Free-Proxies https://github.com/Anonym0usWork1221/Free-Proxies"""

    name = "anonym0uswork"
    url = "https://github.com/Anonym0usWork1221/Free-Proxies"

    enabled = True

    SOURCES = (
        "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/http_proxies.txt",
        "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/socks4_proxies.txt",
        "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/socks5_proxies.txt",
    )

    def fetch(self):
        proxies = []
        for source_url in self.SOURCES:
            try:
                r = WebRequest().get(source_url, timeout=10, retry_time=1)
                proxies.extend(self.parseProxiesFromText(r.text))
            except Exception as e:
                logger.error("ProxyFetch - anonym0uswork (%s): %s" % (source_url, e))
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in Anonym0usWorkFetcher().fetch():
        print(proxy)
