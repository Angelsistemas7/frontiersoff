# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     thespeedx.py
   Description :   TheSpeedX/PROXY-List 代理源 (cobertura global)
   Author :        Claude
   date：          2026/07/11
-------------------------------------------------
"""
__author__ = 'Claude'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class TheSpeedXFetcher(BaseFetcher):
    """TheSpeedX/PROXY-List https://github.com/TheSpeedX/PROXY-List"""

    name = "thespeedx"
    url = "https://github.com/TheSpeedX/PROXY-List"

    enabled = True

    SOURCES = (
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    )

    def fetch(self):
        proxies = []
        for source_url in self.SOURCES:
            try:
                r = WebRequest().get(source_url, timeout=10, retry_time=1)
                proxies.extend(self.parseProxiesFromText(r.text))
            except Exception as e:
                logger.error("ProxyFetch - thespeedx (%s): %s" % (source_url, e))
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in TheSpeedXFetcher().fetch():
        print(proxy)
