# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     hideipme.py
   Description :   zloi-user/hideip.me 代理源 (incluye pais, se ignora - solo se usa ip:port)
   Author :        Claude
   date：          2026/07/14
-------------------------------------------------
"""
__author__ = 'Claude'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class HideIpMeFetcher(BaseFetcher):
    """zloi-user/hideip.me https://github.com/zloi-user/hideip.me"""

    name = "hideipme"
    url = "https://github.com/zloi-user/hideip.me"

    enabled = True

    SOURCES = (
        "https://raw.githubusercontent.com/zloi-user/hideip.me/main/http.txt",
    )

    def fetch(self):
        proxies = []
        for source_url in self.SOURCES:
            try:
                r = WebRequest().get(source_url, timeout=10, retry_time=1)
                proxies.extend(self.parseProxiesFromText(r.text))
            except Exception as e:
                logger.error("ProxyFetch - hideipme (%s): %s" % (source_url, e))
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in HideIpMeFetcher().fetch():
        print(proxy)
