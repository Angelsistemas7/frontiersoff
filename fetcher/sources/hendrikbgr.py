# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     hendrikbgr.py
   Description :   hendrikbgr/Free-Proxy-Repo 代理源
   Author :        Claude
   date：          2026/07/14
-------------------------------------------------
"""
__author__ = 'Claude'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class HendrikbgrFetcher(BaseFetcher):
    """hendrikbgr/Free-Proxy-Repo https://github.com/hendrikbgr/Free-Proxy-Repo"""

    name = "hendrikbgr"
    url = "https://github.com/hendrikbgr/Free-Proxy-Repo"

    enabled = True

    SOURCES = (
        "https://raw.githubusercontent.com/hendrikbgr/Free-Proxy-Repo/master/proxy_list.txt",
    )

    def fetch(self):
        proxies = []
        for source_url in self.SOURCES:
            try:
                r = WebRequest().get(source_url, timeout=10, retry_time=1)
                proxies.extend(self.parseProxiesFromText(r.text))
            except Exception as e:
                logger.error("ProxyFetch - hendrikbgr (%s): %s" % (source_url, e))
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in HendrikbgrFetcher().fetch():
        print(proxy)
