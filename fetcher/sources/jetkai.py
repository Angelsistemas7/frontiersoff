# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     jetkai.py
   Description :   jetkai/proxy-list 代理源
   Author :        Claude
   date：          2026/07/12
-------------------------------------------------
"""
__author__ = 'Claude'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class JetkaiFetcher(BaseFetcher):
    """jetkai/proxy-list https://github.com/jetkai/proxy-list"""

    name = "jetkai"
    url = "https://github.com/jetkai/proxy-list"

    enabled = True

    SOURCES = (
        "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
        "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks4.txt",
        "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt",
    )

    def fetch(self):
        proxies = []
        for source_url in self.SOURCES:
            try:
                r = WebRequest().get(source_url, timeout=10, retry_time=1)
                proxies.extend(self.parseProxiesFromText(r.text))
            except Exception as e:
                logger.error("ProxyFetch - jetkai (%s): %s" % (source_url, e))
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in JetkaiFetcher().fetch():
        print(proxy)
