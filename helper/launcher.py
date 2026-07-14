# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     launcher
   Description :   启动器
   Author :        JHao
   date：          2021/3/26
-------------------------------------------------
   Change Activity:
                   2021/3/26: 启动器
-------------------------------------------------
"""
__author__ = 'JHao'

import sys
from db.dbClient import DbClient
from handler.logHandler import LogHandler
from handler.configHandler import ConfigHandler

log = LogHandler('launcher')


def startServer():
    __beforeStart()
    from api.proxyApi import runFlask
    runFlask()


def startScheduler():
    __beforeStart()
    from helper.scheduler import runScheduler
    runScheduler()


def startOnce():
    """ Un solo ciclo de fetch+check (para runners efimeros tipo CI). Si
    Redis no esta disponible (ej. cuota de Upstash agotada), no se pierde
    lo scrapeado esta corrida - ver __captureFallback. """
    if __beforeStart(fallback=__captureFallback):
        return
    from helper.scheduler import runOnce
    runOnce()


def startShard():
    """ Fetch + check de un pedazo de una fuente (ver PROXY_FETCHER_ONLY +
    SHARD_INDEX/SHARD_COUNT), sin re-validar el pool entero """
    if __beforeStart(fallback=__captureFallback):
        return
    from helper.scheduler import runShard
    runShard()


def __beforeStart(fallback=None):
    __showVersion()
    __showConfigure()
    if __checkDBConfig():
        if fallback:
            log.warning("DB no disponible - usando modo de captura sin Redis (pending_sync/)")
            fallback()
            return True
        log.info('exit!')
        sys.exit()
    return False


def __captureFallback():
    """ Red de seguridad para runners efimeros (CI): si Redis no responde
    (ej. cuota mensual agotada de Upstash), igual se scrapean los
    candidatos (esto no toca Redis para nada) y se guardan en
    pending_sync/ en vez de perderse. La proxima corrida que encuentre
    Redis disponible los recupera solos (ver helper/scheduler.py). """
    from helper import pendingSync
    from helper.fetch import Fetcher
    candidates = [p.proxy for p in Fetcher().run()]
    path = pendingSync.dump(candidates, note="DB no disponible al arrancar")
    if path:
        log.warning("%d candidatos guardados en %s (sin validar, para no perderlos)" % (len(candidates), path))
    else:
        log.warning("no se encontraron candidatos para guardar esta corrida")


def __showVersion():
    from setting import VERSION
    log.info("ProxyPool Version: %s" % VERSION)


def __showConfigure():
    conf = ConfigHandler()
    log.info("ProxyPool configure HOST: %s" % conf.serverHost)
    log.info("ProxyPool configure PORT: %s" % conf.serverPort)
    exclude = conf.fetcherExclude
    if exclude:
        log.info("ProxyPool configure PROXY_FETCHER_EXCLUDE: %s" % exclude)
    only = conf.fetcherOnly
    if only:
        log.info("ProxyPool configure PROXY_FETCHER_ONLY: %s" % only)
    if conf.shardCount > 1:
        log.info("ProxyPool configure SHARD: %s/%s" % (conf.shardIndex, conf.shardCount))
    log.info("ProxyPool configure PROXY_FETCHER: auto-scan (enabled=True, exclude=%s)" % exclude)


def __checkDBConfig():
    conf = ConfigHandler()
    db = DbClient(conf.dbConn)
    log.info("============ DATABASE CONFIGURE ================")
    log.info("DB_TYPE: %s" % db.db_type)
    log.info("DB_HOST: %s" % db.db_host)
    log.info("DB_PORT: %s" % db.db_port)
    log.info("DB_NAME: %s" % db.db_name)
    log.info("DB_USER: %s" % db.db_user)
    log.info("=================================================")
    return db.test()
