# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     Proxy
   Description :   代理对象类型封装
   Author :        JHao
   date：          2019/7/11
-------------------------------------------------
   Change Activity:
                   2019/7/11: 代理对象类型封装
-------------------------------------------------
"""
__author__ = 'JHao'

import json


class Proxy(object):

    def __init__(self, proxy, fail_count=0, region="", anonymous="",
                 source="", check_count=0, last_status="", last_time="", https=False,
                 risk_score=0, risk_reasons=None, risk_strikes=0, trust_status="trusted",
                 reported=False, reported_at="", city="", asn="", isp="", network_type="",
                 latency_ms=0, is_whitelisted=False, socks5=False, ssh_available=False,
                 bandwidth_kbps=0, viewer_safe=False):
        self._proxy = proxy
        self._fail_count = fail_count
        self._region = region
        self._anonymous = anonymous
        self._source = source.split('/')
        self._check_count = check_count
        self._last_status = last_status
        self._last_time = last_time
        self._https = https
        # -------- malicious-detection fields --------
        self._risk_score = risk_score          # 0-100, 0 = sin señales sospechosas
        self._risk_reasons = risk_reasons or [] # lista de {"check","points","detail"}
        self._risk_strikes = risk_strikes       # detecciones consecutivas por encima del umbral
        self._trust_status = trust_status       # trusted | quarantine | malicious
        self._reported = reported               # ya se reporto a AbuseIPDB
        self._reported_at = reported_at
        # -------- geo / ASN --------
        self._city = city
        self._asn = asn                         # ej. "AS15169"
        self._isp = isp
        self._network_type = network_type       # datacenter | residential_or_unknown
        # -------- rotacion / calidad --------
        self._latency_ms = latency_ms           # tiempo de la ultima validacion http, en ms
        self._is_whitelisted = is_whitelisted   # cumple los criterios de "IP sana"
        # -------- protocolos --------
        self._socks5 = socks5                   # tambien responde como SOCKS5 (DNS remoto)
        self._ssh_available = ssh_available     # el host tiene SSH abierto (util p/ nodos propios)
        self._bandwidth_kbps = bandwidth_kbps   # ultima medicion real de ancho de banda (kbps), 0 = nunca medido
        # filtro mas estricto que "trusted": pensado para trafico de gente
        # real (ej. espectadores viendo un stream), no solo el backend
        # propio. Ver helper/check.py::viewerSafeChecker.
        self._viewer_safe = viewer_safe

    @classmethod
    def createFromJson(cls, proxy_json):
        _dict = json.loads(proxy_json)
        return cls(proxy=_dict.get("proxy", ""),
                   fail_count=_dict.get("fail_count", 0),
                   region=_dict.get("region", ""),
                   anonymous=_dict.get("anonymous", ""),
                   source=_dict.get("source", ""),
                   check_count=_dict.get("check_count", 0),
                   last_status=_dict.get("last_status", ""),
                   last_time=_dict.get("last_time", ""),
                   https=_dict.get("https", False),
                   risk_score=_dict.get("risk_score", 0),
                   risk_reasons=_dict.get("risk_reasons", []),
                   risk_strikes=_dict.get("risk_strikes", 0),
                   trust_status=_dict.get("trust_status", "trusted"),
                   reported=_dict.get("reported", False),
                   reported_at=_dict.get("reported_at", ""),
                   city=_dict.get("city", ""),
                   asn=_dict.get("asn", ""),
                   isp=_dict.get("isp", ""),
                   network_type=_dict.get("network_type", ""),
                   latency_ms=_dict.get("latency_ms", 0),
                   is_whitelisted=_dict.get("is_whitelisted", False),
                   socks5=_dict.get("socks5", False),
                   ssh_available=_dict.get("ssh_available", False),
                   bandwidth_kbps=_dict.get("bandwidth_kbps", 0),
                   viewer_safe=_dict.get("viewer_safe", False),
                   )

    @property
    def proxy(self):
        """ 代理 ip:port """
        return self._proxy

    @property
    def fail_count(self):
        """ 检测失败次数 """
        return self._fail_count

    @property
    def region(self):
        """ 地理位置(国家/城市) """
        return self._region

    @property
    def anonymous(self):
        """ 匿名 """
        return self._anonymous

    @property
    def source(self):
        """ 代理来源 """
        return '/'.join(self._source)

    @property
    def check_count(self):
        """ 代理检测次数 """
        return self._check_count

    @property
    def last_status(self):
        """ 最后一次检测结果  True -> 可用; False -> 不可用"""
        return self._last_status

    @property
    def last_time(self):
        """ 最后一次检测时间 """
        return self._last_time

    @property
    def https(self):
        """ 是否支持https """
        return self._https

    @property
    def risk_score(self):
        """ puntaje de riesgo 0-100 (0 = sin señales, >=umbral = sospechoso/malicioso) """
        return self._risk_score

    @property
    def risk_reasons(self):
        """ lista de motivos detectados: [{"check","points","detail"}, ...] """
        return self._risk_reasons

    @property
    def risk_strikes(self):
        """ detecciones consecutivas por encima del umbral de cuarentena """
        return self._risk_strikes

    @property
    def trust_status(self):
        """ trusted | quarantine | malicious """
        return self._trust_status

    @property
    def reported(self):
        """ True si ya se reporto este proxy a AbuseIPDB """
        return self._reported

    @property
    def reported_at(self):
        """ fecha/hora del ultimo reporte a AbuseIPDB """
        return self._reported_at

    @property
    def city(self):
        """ ciudad (geolocalización) """
        return self._city

    @property
    def asn(self):
        """ Autonomous System Number, ej. 'AS15169' """
        return self._asn

    @property
    def isp(self):
        """ ISP / organización dueña del ASN """
        return self._isp

    @property
    def network_type(self):
        """ datacenter | residential_or_unknown (heurística por ASN/ISP) """
        return self._network_type

    @property
    def latency_ms(self):
        """ tiempo (ms) de la última validación http exitosa """
        return self._latency_ms

    @property
    def is_whitelisted(self):
        """ True si cumple los criterios de "IP sana" (ver setting.WHITELIST_*) """
        return self._is_whitelisted

    @property
    def socks5(self):
        """ True si el proxy tambien responde como SOCKS5 (permite DNS remoto) """
        return self._socks5

    @property
    def ssh_available(self):
        """ True si el host tiene un puerto SSH abierto (informativo, util p/ nodos propios) """
        return self._ssh_available

    @property
    def bandwidth_kbps(self):
        """ Ultima medicion real de ancho de banda (kbps). 0 = nunca se midio (no es automatico). """
        return self._bandwidth_kbps

    @property
    def viewer_safe(self):
        """ True si pasa el filtro estricto para trafico de gente real
        (ver helper/check.py::viewerSafeChecker) - no solo "trusted". """
        return self._viewer_safe

    @property
    def to_dict(self):
        """ 属性字典 """
        return {"proxy": self.proxy,
                "https": self.https,
                "fail_count": self.fail_count,
                "region": self.region,
                "anonymous": self.anonymous,
                "source": self.source,
                "check_count": self.check_count,
                "last_status": self.last_status,
                "last_time": self.last_time,
                "risk_score": self.risk_score,
                "risk_reasons": self.risk_reasons,
                "risk_strikes": self.risk_strikes,
                "trust_status": self.trust_status,
                "reported": self.reported,
                "reported_at": self.reported_at,
                "city": self.city,
                "asn": self.asn,
                "isp": self.isp,
                "network_type": self.network_type,
                "latency_ms": self.latency_ms,
                "is_whitelisted": self.is_whitelisted,
                "socks5": self.socks5,
                "ssh_available": self.ssh_available,
                "bandwidth_kbps": self.bandwidth_kbps,
                "viewer_safe": self.viewer_safe}

    @property
    def to_json(self):
        """ 属性json格式 """
        return json.dumps(self.to_dict, ensure_ascii=False)

    @fail_count.setter
    def fail_count(self, value):
        self._fail_count = value

    @check_count.setter
    def check_count(self, value):
        self._check_count = value

    @last_status.setter
    def last_status(self, value):
        self._last_status = value

    @last_time.setter
    def last_time(self, value):
        self._last_time = value

    @https.setter
    def https(self, value):
        self._https = value

    @region.setter
    def region(self, value):
        self._region = value

    @risk_score.setter
    def risk_score(self, value):
        self._risk_score = value

    @risk_reasons.setter
    def risk_reasons(self, value):
        self._risk_reasons = value

    @risk_strikes.setter
    def risk_strikes(self, value):
        self._risk_strikes = value

    @trust_status.setter
    def trust_status(self, value):
        self._trust_status = value

    @reported.setter
    def reported(self, value):
        self._reported = value

    @reported_at.setter
    def reported_at(self, value):
        self._reported_at = value

    @city.setter
    def city(self, value):
        self._city = value

    @asn.setter
    def asn(self, value):
        self._asn = value

    @isp.setter
    def isp(self, value):
        self._isp = value

    @network_type.setter
    def network_type(self, value):
        self._network_type = value

    @latency_ms.setter
    def latency_ms(self, value):
        self._latency_ms = value

    @is_whitelisted.setter
    def is_whitelisted(self, value):
        self._is_whitelisted = value

    @socks5.setter
    def socks5(self, value):
        self._socks5 = value

    @ssh_available.setter
    def ssh_available(self, value):
        self._ssh_available = value

    @bandwidth_kbps.setter
    def bandwidth_kbps(self, value):
        self._bandwidth_kbps = value

    @viewer_safe.setter
    def viewer_safe(self, value):
        self._viewer_safe = value

    def add_source(self, source_str):
        if source_str:
            self._source.append(source_str)
            self._source = list(set(self._source))
