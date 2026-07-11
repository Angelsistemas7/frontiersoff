# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     clarketm.py
   Description :   clarketm/proxy-list 代理源 (cobertura global)
   Author :        Claude
   date：          2026/07/11
-------------------------------------------------
"""
__author__ = 'Claude'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class ClarketmFetcher(BaseFetcher):
    """clarketm/proxy-list https://github.com/clarketm/proxy-list"""

    name = "clarketm"
    url = "https://github.com/clarketm/proxy-list"

    enabled = True

    def fetch(self):
        url = "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt"
        try:
            r = WebRequest().get(url, timeout=10, retry_time=1)
            for proxy in self.yieldUniqueProxies(self.parseProxiesFromText(r.text)):
                yield proxy
        except Exception as e:
            logger.error("ProxyFetch - clarketm: %s" % e)


if __name__ == '__main__':
    for proxy in ClarketmFetcher().fetch():
        print(proxy)
