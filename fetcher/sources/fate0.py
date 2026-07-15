# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     fate0.py
   Description :   fate0/proxylist 代理源 (formato JSON lines - un objeto
                    JSON por linea, no un array - parseo dedicado)
   Author :        Claude
   date：          2026/07/14
-------------------------------------------------
"""
import json

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class Fate0Fetcher(BaseFetcher):
    """fate0/proxylist https://github.com/fate0/proxylist"""

    name = "fate0"
    url = "https://github.com/fate0/proxylist"

    enabled = True

    SOURCES = (
        "https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list",
    )

    def fetch(self):
        proxies = []
        for source_url in self.SOURCES:
            try:
                r = WebRequest().get(source_url, timeout=10, retry_time=1)
                for line in r.text.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        item = json.loads(line)
                    except ValueError:
                        continue
                    host, port = item.get("host"), item.get("port")
                    if host and port:
                        proxies.append("%s:%s" % (host, port))
            except Exception as e:
                logger.error("ProxyFetch - fate0 (%s): %s" % (source_url, e))
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in Fate0Fetcher().fetch():
        print(proxy)
