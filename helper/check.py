# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     check
   Description :   执行代理校验
   Author :        JHao
   date：          2019/8/6
-------------------------------------------------
   Change Activity:
                   2019/08/06: 执行代理校验
                   2021/05/25: 分别校验http和https
                   2022/08/16: 获取代理Region信息
-------------------------------------------------
"""
__author__ = 'JHao'

import time
from util.six import Empty
from threading import Thread
from datetime import datetime
from handler.logHandler import LogHandler
from helper.validator import ProxyValidator
from helper import maliciousDetector
from helper import abuseReporter
from helper import geoAsn
from helper import netutil
from helper import protocolChecker
from handler.proxyHandler import ProxyHandler
from handler.riskHandler import RiskHandler
from handler.configHandler import ConfigHandler


class DoValidator(object):
    """ 执行校验 """

    conf = ConfigHandler()

    @classmethod
    def validator(cls, proxy, work_type):
        """
        校验入口
        Args:
            proxy: Proxy Object
            work_type: raw/use
        Returns:
            Proxy Object
        """
        start = time.time()
        http_r = cls.httpValidator(proxy)
        elapsed_ms = int((time.time() - start) * 1000)
        https_r = False if not http_r else cls.httpsValidator(proxy)

        proxy.check_count += 1
        proxy.last_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        proxy.last_status = True if http_r else False
        if http_r:
            proxy.latency_ms = elapsed_ms
            if proxy.fail_count > 0:
                proxy.fail_count -= 1
            proxy.https = True if https_r else False
            if work_type == "raw":
                if cls.conf.proxyRegion:
                    cls.geoAsnSetter(proxy)
                cls.protocolSetter(proxy)
                cls.sshSetter(proxy)
            cls.maliciousChecker(proxy)
            cls.whitelistChecker(proxy)
            cls.viewerSafeChecker(proxy)
        else:
            proxy.fail_count += 1
        return proxy

    @classmethod
    def maliciousChecker(cls, proxy):
        """
        Evalúa señales de manipulación de tráfico y actualiza el estado de
        confianza del proxy. No es un descarte binario: usa un puntaje de
        riesgo (0-100) y dos umbrales, y solo confirma "malicioso" tras
        varias detecciones consecutivas por encima del umbral alto
        (evita descartar/reportar por un único falso positivo).
        """
        try:
            score, reasons = maliciousDetector.inspect(proxy.proxy)
        except Exception as e:
            cls.log_malicious_error(e)
            return  # inconcluso: no se toca el trust_status vigente

        proxy.risk_score = score
        proxy.risk_reasons = reasons

        if score >= cls.conf.maliciousConfirmThreshold:
            proxy.risk_strikes += 1
        elif score < cls.conf.maliciousQuarantineThreshold:
            proxy.risk_strikes = 0
        # entre los dos umbrales: sospechoso pero no se suma ni resetea el contador

        if proxy.risk_strikes >= cls.conf.maliciousConfirmStrikes:
            proxy.trust_status = "malicious"
        elif score >= cls.conf.maliciousQuarantineThreshold:
            proxy.trust_status = "quarantine"
        else:
            proxy.trust_status = "trusted"

    @classmethod
    def log_malicious_error(cls, e):
        LogHandler("checker").error("malicious detector error: %s" % str(e))

    @classmethod
    def whitelistChecker(cls, proxy):
        """
        "IP sana": confiable, con varias validaciones seguidas sin fallar,
        y latencia dentro de lo razonable. Se re-evalúa en cada check, así
        que un proxy puede entrar y salir de la lista blanca con el tiempo.
        """
        proxy.is_whitelisted = (
            proxy.trust_status == "trusted"
            and proxy.check_count >= cls.conf.whitelistMinChecks
            and proxy.fail_count == 0
            and 0 < proxy.latency_ms <= cls.conf.whitelistMaxLatencyMs
        )

    @classmethod
    def viewerSafeChecker(cls, proxy):
        """
        Filtro mas estricto que "trusted"/whitelist, pensado para proxies
        que va a usar gente real (ej. espectadores viendo un stream), no
        solo el backend propio. Un proxy scrapeado necesita: cero señales
        de riesgo en el chequeo actual, nunca haber confirmado una
        detección de manipulación, varias validaciones limpias seguidas, Y
        un ancho de banda real medido (no automatico, hay que haber
        corrido /bandwidth/test/ en algun momento). Los nodos propios
        ("own:...") se eximen del minimo de checks/bandwidth - se asume
        que ya confias en tu propia infraestructura - pero igual deben
        estar "trusted" y sin ninguna señal de riesgo.
        """
        is_own = any(s.startswith('own:') for s in proxy.source.split('/'))
        base_ok = (
            proxy.trust_status == "trusted"
            and proxy.risk_score == 0
            and proxy.risk_strikes == 0
            and proxy.fail_count == 0
        )
        if is_own:
            proxy.viewer_safe = base_ok
        else:
            proxy.viewer_safe = (
                base_ok
                and proxy.check_count >= cls.conf.viewerSafeMinChecks
                and proxy.bandwidth_kbps >= cls.conf.viewerSafeMinBandwidthKbps
            )

    @classmethod
    def httpValidator(cls, proxy):
        for func in ProxyValidator.http_validator:
            if not func(proxy.proxy):
                return False
        return True

    @classmethod
    def httpsValidator(cls, proxy):
        for func in ProxyValidator.https_validator:
            if not func(proxy.proxy):
                return False
        return True

    @classmethod
    def preValidator(cls, proxy):
        for func in ProxyValidator.pre_validator:
            if not func(proxy):
                return False
        return True

    @classmethod
    def geoAsnSetter(cls, proxy):
        """ país/ciudad/ASN/ISP + clasificación datacenter vs residencial-o-desconocido """
        ip = netutil.extractHost(proxy.proxy)
        info = geoAsn.lookup(ip)
        proxy.region = info.get("country", "error")
        proxy.city = info.get("city", "")
        proxy.asn = info.get("asn", "")
        proxy.isp = info.get("isp", "")
        proxy.network_type = info.get("network_type", "")

    @classmethod
    def protocolSetter(cls, proxy):
        """ Detecta si el proxy tambien responde como SOCKS5 (ademas de HTTP/HTTPS) """
        proxy.socks5 = protocolChecker.checkSocks5(proxy.proxy, timeout=cls.conf.verifyTimeout)

    @classmethod
    def sshSetter(cls, proxy):
        """ Informativo: el host tambien tiene SSH abierto? (ver protocolChecker.checkSshBanner) """
        host = netutil.extractHost(proxy.proxy)
        proxy.ssh_available = protocolChecker.checkSshBanner(host)


class _ThreadChecker(Thread):
    """ 多线程检测 """

    def __init__(self, work_type, target_queue, thread_name):
        Thread.__init__(self, name=thread_name)
        self.work_type = work_type
        self.log = LogHandler("checker")
        self.proxy_handler = ProxyHandler()
        self.risk_handler = RiskHandler()
        self.target_queue = target_queue
        self.conf = ConfigHandler()

    def run(self):
        self.log.info("{}ProxyCheck - {}: start".format(self.work_type.title(), self.name))
        while True:
            try:
                proxy = self.target_queue.get(block=False)
            except Empty:
                self.log.info("{}ProxyCheck - {}: complete".format(self.work_type.title(), self.name))
                break
            proxy = DoValidator.validator(proxy, self.work_type)
            if self.work_type == "raw":
                self.__ifRaw(proxy)
            else:
                self.__ifUse(proxy)
            self.target_queue.task_done()

    def __ifRaw(self, proxy):
        if proxy.last_status:
            # el chequeo de "ya lo conocemos?" se hace EN LOTE, antes de
            # validar, en helper/scheduler.py::__runProxyFetch (3 comandos
            # Redis para TODOS los candidatos, en vez de 3 por candidato) - ver
            # el comentario ahi para el porque. Si un proxy llega hasta aca es
            # porque ya se filtro como nuevo.
            self.log.info('RawProxyCheck - {}: {} pass ({})'.format(
                self.name, proxy.proxy.ljust(23), proxy.trust_status))
            self.__route(proxy)
        else:
            self.log.info('RawProxyCheck - {}: {} fail'.format(self.name, proxy.proxy.ljust(23)))

    def __ifUse(self, proxy):
        if proxy.last_status:
            self.log.info('UseProxyCheck - {}: {} pass ({})'.format(
                self.name, proxy.proxy.ljust(23), proxy.trust_status))
            self.__route(proxy)
        else:
            if proxy.fail_count > self.conf.maxFailCount:
                self.log.info('UseProxyCheck - {}: {} fail, count {} delete'.format(self.name,
                                                                                    proxy.proxy.ljust(23),
                                                                                    proxy.fail_count))
                self.proxy_handler.delete(proxy)
                self.risk_handler.deleteQuarantine(proxy)
            else:
                self.log.info('UseProxyCheck - {}: {} fail, count {} keep'.format(self.name,
                                                                                  proxy.proxy.ljust(23),
                                                                                  proxy.fail_count))
                # no hubo señal nueva de confianza esta ronda: se queda en la tabla donde estaba
                if proxy.trust_status == "quarantine":
                    self.risk_handler.putQuarantine(proxy)
                else:
                    self.proxy_handler.put(proxy)

    def __route(self, proxy):
        """ Ubica el proxy en la tabla que corresponde a su trust_status vigente """
        if proxy.trust_status == "malicious":
            reasons = "; ".join(r["detail"] for r in proxy.risk_reasons)
            self.log.warning('MaliciousProxy - {}: {} score={} -> {}'.format(
                self.name, proxy.proxy.ljust(23), proxy.risk_score, reasons))
            self.proxy_handler.delete(proxy)
            self.risk_handler.deleteQuarantine(proxy)
            if not proxy.reported and abuseReporter.report(proxy):
                proxy.reported = True
                proxy.reported_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.risk_handler.putMalicious(proxy)
        elif proxy.trust_status == "quarantine":
            self.log.info('QuarantineProxy - {}: {} score={}'.format(
                self.name, proxy.proxy.ljust(23), proxy.risk_score))
            self.proxy_handler.delete(proxy)
            self.risk_handler.putQuarantine(proxy)
        else:
            self.risk_handler.deleteQuarantine(proxy)
            self.risk_handler.deleteMalicious(proxy)
            self.proxy_handler.put(proxy)


def Checker(tp, queue):
    """
    run Proxy ThreadChecker
    :param tp: raw/use
    :param queue: Proxy Queue
    :return:
    """
    conf = ConfigHandler()
    log = LogHandler("checker")
    thread_count = conf.checkThreadCount
    thread_list = list()
    for index in range(thread_count):
        thread_list.append(_ThreadChecker(tp, queue, "thread_%s" % str(index).zfill(2)))

    for thread in thread_list:
        thread.setDaemon(True)
        thread.start()

    # mismo motivo que en helper/fetch.py: aunque cada chequeo individual ya
    # tiene su propio timeout de red, un join() sin limite significa que un
    # solo hilo trabado bloquearia la validacion entera para siempre. Red de
    # seguridad extra, no la causa principal de la lentitud (esa es volumen).
    for thread in thread_list:
        thread.join(timeout=conf.checkThreadJoinTimeout)
        if thread.is_alive():
            log.error("Checker - %s: no termino en %ss, se sigue sin esperarlo" % (
                thread.name, conf.checkThreadJoinTimeout))
