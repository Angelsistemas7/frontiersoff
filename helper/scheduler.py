# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyScheduler
   Description :
   Author :        JHao
   date：          2019/8/5
-------------------------------------------------
   Change Activity:
                   2019/08/05: proxyScheduler
                   2021/02/23: runProxyCheck时,剩余代理少于POOL_SIZE_MIN时执行抓取
-------------------------------------------------
"""
__author__ = 'JHao'

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ProcessPoolExecutor

from util.six import Queue
from helper.fetch import Fetcher
from helper.check import Checker
from handler.logHandler import LogHandler
from handler.proxyHandler import ProxyHandler
from handler.riskHandler import RiskHandler
from handler.controlHandler import ControlHandler
from handler.configHandler import ConfigHandler

scheduler_log = LogHandler("scheduler")


def __runProxyFetch():
    control = ControlHandler()
    if control.is_paused():
        scheduler_log.info("proxy_fetch: paused, skip")
        return
    proxy_fetcher = Fetcher()
    candidates = list(proxy_fetcher.run())

    # Filtro EN LOTE de "ya lo conocemos" ANTES de validar nada - bug real
    # de produccion: antes este chequeo se hacia por candidato DESPUES de
    # la validacion completa (HTTP real + detector de maliciosos), uno por
    # uno via 3 comandos Redis c/u (exists en use/quarantine/malicious).
    # Con los ~100k candidatos de MuRongPIG eso solo explicaba la enorme
    # mayoria de los comandos consumidos contra la cuota gratis de Upstash
    # (confirmado en su panel: 984,723 reads vs 15,277 writes en un mes).
    # Ahora: 3 comandos Redis TOTALES (uno por tabla, para todos los
    # candidatos juntos) para saber cuales filtrar, y encima se ahorra la
    # validacion real (red, detector) de los que ya conociamos.
    proxy_handler = ProxyHandler()
    risk_handler = RiskHandler()
    already_known = (proxy_handler.existsMany(candidates)
                      | risk_handler.existsManyQuarantine(candidates)
                      | risk_handler.existsManyMalicious(candidates))
    new_candidates = [p for p in candidates if p.proxy not in already_known]
    scheduler_log.info("proxy_fetch: %d candidatos, %d ya conocidos (filtrados en lote), %d nuevos a validar" % (
        len(candidates), len(already_known), len(new_candidates)))

    proxy_queue = Queue()
    for proxy in new_candidates:
        proxy_queue.put(proxy)

    Checker("raw", proxy_queue)
    control.mark_fetch()


def __runProxyCheck():
    control = ControlHandler()
    if control.is_paused():
        scheduler_log.info("proxy_check: paused, skip")
        return
    proxy_handler = ProxyHandler()
    risk_handler = RiskHandler()
    proxy_queue = Queue()
    if proxy_handler.db.getCount().get("total", 0) < proxy_handler.conf.poolSizeMin:
        __runProxyFetch()
    for proxy in proxy_handler.getAll():
        proxy_queue.put(proxy)
    # los proxies en cuarentena también se re-evalúan: pueden recuperar
    # confianza (vuelven al pool normal) o confirmarse como maliciosos.
    for proxy in risk_handler.getAllQuarantine():
        proxy_queue.put(proxy)
    Checker("use", proxy_queue)
    control.mark_check()


def runOnce():
    """ Un solo ciclo de fetch+check y termina, sin quedar corriendo. Pensado
    para entornos efimeros (ej. un workflow de GitHub Actions con cron): el
    runner hace su trabajo con una IP de salida que no es la de tu red, y se
    apaga solo — nada que mantener corriendo ni que rastrear a tu casa. """
    scheduler_log.info("runOnce: ciclo unico (fetch + check), sin scheduler persistente")
    __runProxyFetch()
    __runProxyCheck()
    scheduler_log.info("runOnce: listo")


def runShard():
    """ Como runOnce() pero SOLO fetch + validacion de lo recien traido -
    sin re-chequear el pool entero. Pensado para jobs de Actions en
    paralelo (matrix) que procesan un pedazo de una fuente de mucho
    volumen (ver PROXY_FETCHER_ONLY + SHARD_INDEX/SHARD_COUNT en
    ConfigHandler): si cada uno de los N jobs paralelos ademas re-validara
    el pool entero compartido, seria trabajo redundante multiplicado por N. """
    scheduler_log.info("runShard: fetch + check de un pedazo, sin re-validar el pool entero")
    __runProxyFetch()
    scheduler_log.info("runShard: listo")


def runScheduler():
    __runProxyFetch()

    timezone = ConfigHandler().timezone
    scheduler = BlockingScheduler(logger=scheduler_log, timezone=timezone)

    scheduler.add_job(__runProxyFetch, 'interval', minutes=5, id="proxy_fetch", name="proxy采集")
    scheduler.add_job(__runProxyCheck, 'interval', minutes=2, id="proxy_check", name="proxy检查")
    executors = {
        'default': {'type': 'threadpool', 'max_workers': 20},
        'processpool': ProcessPoolExecutor(max_workers=5)
    }
    job_defaults = {
        'coalesce': False,
        'max_instances': 10
    }

    scheduler.configure(executors=executors, job_defaults=job_defaults, timezone=timezone)

    scheduler.start()


if __name__ == '__main__':
    runScheduler()
