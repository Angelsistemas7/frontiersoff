# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     obcbo.py
   Description :   ObcbO/getproxy 代理源 (volumen alto, http)
   Author :        Claude
   date：          2026/07/14
-------------------------------------------------
"""
__author__ = 'Claude'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class ObcbOFetcher(BaseFetcher):
    """ObcbO/getproxy https://github.com/ObcbO/getproxy"""

    name = "obcbo"
    url = "https://github.com/ObcbO/getproxy"

    enabled = True

    SOURCES = (
        "https://raw.githubusercontent.com/ObcbO/getproxy/master/file/http.txt",
    )

    def fetch(self):
        proxies = []
        for source_url in self.SOURCES:
            try:
                r = WebRequest().get(source_url, timeout=10, retry_time=1)
                proxies.extend(self.parseProxiesFromText(r.text))
            except Exception as e:
                logger.error("ProxyFetch - obcbo (%s): %s" % (source_url, e))
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in ObcbOFetcher().fetch():
        print(proxy)
