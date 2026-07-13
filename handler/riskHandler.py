# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     riskHandler
   Description :   CRUD para las tablas quarantine_proxy / malicious_proxy.
                    Usa su propia conexión (no la del DbClient singleton) para
                    poder operar sobre una tabla distinta a la del pool
                    principal sin pisar su estado.
   Author :        Claude
   date：          2026/07/10
-------------------------------------------------
"""
from util.six import urlparse
from helper.proxy import Proxy
from handler.configHandler import ConfigHandler
from util.redisUri import isTlsScheme

QUARANTINE_TABLE = "quarantine_proxy"
MALICIOUS_TABLE = "malicious_proxy"


def _build_client(db_conn, table_name):
    db_conf = urlparse(db_conn)
    scheme = db_conf.scheme.upper().strip()
    # "rediss://" (TLS, lo exigen proveedores gratis como Upstash) es REDIS
    # normal + flag ssl aparte, igual que en db/dbClient.py.
    db_type = "REDIS" if scheme == "REDISS" else scheme
    kwargs = dict(host=db_conf.hostname, port=db_conf.port,
                  username=db_conf.username, password=db_conf.password,
                  db=db_conf.path[1:])
    if db_type == "REDIS":
        from db.redisClient import RedisClient
        kwargs["ssl"] = isTlsScheme(scheme)
        client = RedisClient(**kwargs)
    elif db_type == "SSDB":
        from db.ssdbClient import SsdbClient
        client = SsdbClient(**kwargs)
    else:
        raise AssertionError("type error, Not support DB type: %s" % db_type)
    client.changeTable(table_name)
    return client


class RiskHandler(object):
    """ CRUD de proxies en cuarentena y confirmados como maliciosos """

    def __init__(self):
        self.conf = ConfigHandler()
        self.quarantine = _build_client(self.conf.dbConn, QUARANTINE_TABLE)
        self.malicious = _build_client(self.conf.dbConn, MALICIOUS_TABLE)

    # ---------------- quarantine ----------------
    def putQuarantine(self, proxy):
        self.quarantine.put(proxy)

    def deleteQuarantine(self, proxy):
        return self.quarantine.delete(proxy.proxy)

    def existsQuarantine(self, proxy):
        return self.quarantine.exists(proxy.proxy)

    def existsManyQuarantine(self, proxies):
        """ Version en LOTE - ver db/redisClient.py::existsMany. """
        return self.quarantine.existsMany([p.proxy for p in proxies])

    def getAllQuarantine(self):
        items = self.quarantine.getAll(https=False)
        return [Proxy.createFromJson(_) for _ in items]

    # ---------------- malicious ----------------
    def putMalicious(self, proxy):
        self.malicious.put(proxy)

    def deleteMalicious(self, proxy):
        return self.malicious.delete(proxy.proxy)

    def existsMalicious(self, proxy):
        return self.malicious.exists(proxy.proxy)

    def existsManyMalicious(self, proxies):
        """ Version en LOTE - ver db/redisClient.py::existsMany. """
        return self.malicious.existsMany([p.proxy for p in proxies])

    def getAllMalicious(self):
        items = self.malicious.getAll(https=False)
        return [Proxy.createFromJson(_) for _ in items]
