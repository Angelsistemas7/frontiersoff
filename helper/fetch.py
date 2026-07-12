# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     fetch.py
   Description :   代理采集
   Author :        JHao
   date：          2019/8/6
-------------------------------------------------
   Change Activity:
                   2019/08/06: 多线程采集
                   2026/05/31: 重构为动态加载 fetcher 插件
-------------------------------------------------
"""
__author__ = 'JHao'

import os
import sys
import zlib
import importlib
from threading import Thread

from helper.proxy import Proxy
from helper.check import DoValidator
from handler.logHandler import LogHandler
from handler.configHandler import ConfigHandler
from fetcher.baseFetcher import BaseFetcher

_logger = LogHandler("fetch")

# 模块缓存: {module_name: (mtime, module)}
_module_cache = {}


def _get_sources_dir():
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)), '..', 'fetcher', 'sources')


def _load_module(module_name, filepath):
    """加载或 reload 模块，仅在文件 mtime 变化时 reload"""
    global _module_cache
    mtime = os.path.getmtime(filepath)
    cached = _module_cache.get(module_name)
    if cached and cached[0] == mtime:
        return cached[1]
    try:
        if module_name in sys.modules:
            module = importlib.reload(sys.modules[module_name])
        else:
            module = importlib.import_module(module_name)
        _module_cache[module_name] = (mtime, module)
        return module
    except Exception as e:
        _logger.warning("ProxyFetch : load %s error - %s" % (module_name, e))
        return None


def _discover_fetchers(exclude_list):
    """
    自动扫描 sources/ 目录，返回所有 enabled=True 且不在黑名单中的 fetcher 类列表。
    仅在文件 mtime 变化时重新加载模块，支持运行时热更新。
    """
    global _module_cache
    sources_dir = _get_sources_dir()
    fetcher_classes = []
    seen_modules = set()

    for filename in os.listdir(sources_dir):
        if not filename.endswith('.py') or filename.startswith('_'):
            continue
        module_name = "fetcher.sources.%s" % filename[:-3]
        seen_modules.add(module_name)
        filepath = os.path.join(sources_dir, filename)
        module = _load_module(module_name, filepath)
        if module is None:
            continue
        for attr_name in dir(module):
            attr = getattr(module, attr_name, None)
            if (attr and isinstance(attr, type)
                    and issubclass(attr, BaseFetcher)
                    and attr is not BaseFetcher
                    and attr.name
                    and attr.enabled
                    and attr.__name__ not in exclude_list):
                fetcher_classes.append(attr)

    # 清理已删除文件的缓存
    for name in list(_module_cache):
        if name not in seen_modules:
            del _module_cache[name]

    return sorted(fetcher_classes, key=lambda c: c.name)


class _ThreadFetcher(Thread):

    def __init__(self, fetcher_class, proxy_dict):
        Thread.__init__(self)
        self.fetcher_class = fetcher_class
        self.proxy_dict = proxy_dict
        self.log = LogHandler("fetcher")

    def run(self):
        fetcher_name = self.fetcher_class.name
        self.log.info("ProxyFetch - {func}: start".format(func=fetcher_name))
        try:
            for proxy in self.fetcher_class().fetch():
                self.log.info('ProxyFetch - %s: %s ok' % (fetcher_name, proxy.ljust(23)))
                proxy = proxy.strip()
                if proxy in self.proxy_dict:
                    self.proxy_dict[proxy].add_source(fetcher_name)
                else:
                    self.proxy_dict[proxy] = Proxy(
                        proxy, source=fetcher_name)
        except Exception as e:
            self.log.error("ProxyFetch - {func}: error".format(func=fetcher_name))
            self.log.error(str(e))


class Fetcher(object):
    name = "fetcher"

    def __init__(self):
        self.log = LogHandler(self.name)
        self.conf = ConfigHandler()

    def run(self):
        """
        fetch proxy with fetcher plugins
        :return:
        """
        proxy_dict = dict()
        thread_list = list()
        self.log.info("ProxyFetch : start")

        exclude_list = self.conf.fetcherExclude
        fetcher_classes = _discover_fetchers(exclude_list)

        # PROXY_FETCHER_ONLY (opuesto a exclude): si esta seteado, corre
        # SOLO esas fuentes. Pensado para jobs de Actions en paralelo que
        # procesan una sola fuente de mucho volumen en pedazos (ver
        # shardCount/shardIndex mas abajo) - no tiene sentido que cada
        # pedazo tambien vuelva a traer las otras 24 fuentes.
        only_list = self.conf.fetcherOnly
        if only_list:
            fetcher_classes = [c for c in fetcher_classes if c.__name__ in only_list]

        self.log.info("ProxyFetch : active fetchers [%s]" % ", ".join(c.name for c in fetcher_classes))

        for fetcher_class in fetcher_classes:
            thread_list.append(_ThreadFetcher(fetcher_class, proxy_dict))

        for thread in thread_list:
            thread.setDaemon(True)
            thread.start()

        # Cada fuente ya tiene su propio timeout de red (via WebRequest,
        # 5-10s x reintentos), pero eso no cubre TODOS los casos: una
        # resolucion DNS que se cuelga, o un stall a nivel TCP, puede
        # bloquear un hilo mucho mas alla de su timeout configurado (visto
        # en produccion: un ciclo entero colgado 10+ minutos sin avanzar,
        # con CPU casi en cero - consistente con un hilo esperando I/O que
        # nunca vuelve). Como se espera a TODOS los hilos antes de seguir,
        # un solo fetcher trabado bloqueaba el pool entero indefinidamente.
        # Por eso hay un limite duro por hilo: si no termino a tiempo, se
        # sigue sin el (queda como daemon, muere solo cuando el proceso
        # termine) en vez de esperarlo para siempre.
        for thread in thread_list:
            thread.join(timeout=self.conf.fetchThreadJoinTimeout)
            if thread.is_alive():
                self.log.error(
                    "ProxyFetch - %s: no termino en %ss, se sigue sin esperarlo "
                    "(datos parciales si ya trajo algo)" % (
                        thread.fetcher_class.name, self.conf.fetchThreadJoinTimeout))

        self.log.info("ProxyFetch - all complete!")

        # Sharding: para fuentes de mucho volumen (ej. murongpig, ~100k
        # candidatos, no entra en una sola corrida acotada de Actions) se
        # puede dividir el trabajo en N pedazos deterministas, cada uno
        # corriendo en un job de Actions distinto (matrix), con su propia
        # IP efimera. crc32 en vez del hash() nativo de Python: hash() de
        # strings esta "salado" al azar en cada proceso (proteccion contra
        # DoS de hashing), asi que el mismo proxy caeria en un pedazo
        # distinto en cada job - crc32 es estable entre procesos.
        shard_count = self.conf.shardCount
        shard_index = self.conf.shardIndex
        skipped_shard = 0
        for proxy_obj in proxy_dict.values():
            if shard_count > 1 and (zlib.crc32(proxy_obj.proxy.encode()) % shard_count) != shard_index:
                skipped_shard += 1
                continue
            if DoValidator.preValidator(proxy_obj.proxy):
                yield proxy_obj
        if shard_count > 1:
            self.log.info("ProxyFetch : shard %s/%s - %s candidatos fuera de este pedazo" % (
                shard_index, shard_count, skipped_shard))
