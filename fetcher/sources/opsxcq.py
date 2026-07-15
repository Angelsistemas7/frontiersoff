# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     opsxcq.py
   Description :   opsxcq/proxy-list 代理源
   Author :        Claude
   date：          2026/07/14
-------------------------------------------------
"""
__author__ = 'Claude'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class OpsxcqFetcher(BaseFetcher):
    """opsxcq/proxy-list https://github.com/opsxcq/proxy-list"""

    name = "opsxcq"
    url = "https://github.com/opsxcq/proxy-list"

    enabled = True

    SOURCES = (
        "https://raw.githubusercontent.com/opsxcq/proxy-list/master/list.txt",
    )

    def fetch(self):
        proxies = []
        for source_url in self.SOURCES:
            try:
                r = WebRequest().get(source_url, timeout=10, retry_time=1)
                proxies.extend(self.parseProxiesFromText(r.text))
            except Exception as e:
                logger.error("ProxyFetch - opsxcq (%s): %s" % (source_url, e))
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in OpsxcqFetcher().fetch():
        print(proxy)
