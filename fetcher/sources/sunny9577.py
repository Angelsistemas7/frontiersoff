# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     sunny9577.py
   Description :   sunny9577/proxy-scraper 代理源
   Author :        Claude
   date：          2026/07/12
-------------------------------------------------
"""
__author__ = 'Claude'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class Sunny9577Fetcher(BaseFetcher):
    """sunny9577/proxy-scraper https://github.com/sunny9577/proxy-scraper"""

    name = "sunny9577"
    url = "https://github.com/sunny9577/proxy-scraper"

    enabled = True

    def fetch(self):
        proxies = []
        try:
            r = WebRequest().get(
                "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt",
                timeout=10, retry_time=1)
            proxies.extend(self.parseProxiesFromText(r.text))
        except Exception as e:
            logger.error("ProxyFetch - sunny9577: %s" % str(e))
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in Sunny9577Fetcher().fetch():
        print(proxy)
