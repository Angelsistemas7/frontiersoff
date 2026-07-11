# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyscrape.py
   Description :   ProxyScrape API 代理源 (cobertura global, sin filtro de pais)
   Author :        Claude
   date：          2026/07/11
-------------------------------------------------
"""
__author__ = 'Claude'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class ProxyScrapeFetcher(BaseFetcher):
    """ProxyScrape https://proxyscrape.com"""

    name = "proxyscrape"
    url = "https://proxyscrape.com"

    enabled = True

    SOURCES = (
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all",
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout=10000&country=all",
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000&country=all",
    )

    def fetch(self):
        proxies = []
        for source_url in self.SOURCES:
            try:
                r = WebRequest().get(source_url, timeout=10, retry_time=1)
                proxies.extend(self.parseProxiesFromText(r.text))
            except Exception as e:
                logger.error("ProxyFetch - proxyscrape (%s): %s" % (source_url, e))
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in ProxyScrapeFetcher().fetch():
        print(proxy)
