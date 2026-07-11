# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     netutil
   Description :   Parseo de "proxy_str" compartido por el resto del
                    codigo (formatos 'ip:port', 'user:pass@ip:port', y
                    sus equivalentes IPv6 con notacion entre corchetes
                    '[2001:db8::1]:8080'). Antes cada modulo hacia su
                    propio split(':') ad-hoc, lo cual rompe con IPv6
                    (que tiene multiples ':' en el host).
   Author :        Claude
   date：          2026/07/11
-------------------------------------------------
"""


def stripAuth(proxy_str):
    """ 'user:pass@[::1]:80' -> '[::1]:80'; 'ip:port' -> 'ip:port' (sin cambios) """
    return proxy_str.rsplit('@', 1)[-1] if '@' in proxy_str else proxy_str


def splitHostPort(hostport):
    """
    IPv6-safe.
        '1.2.3.4:80'   -> ('1.2.3.4', 80)
        '[::1]:80'     -> ('::1', 80)
        '[2001:db8::1]:8080' -> ('2001:db8::1', 8080)
    """
    if hostport.startswith('['):
        host, _, port = hostport.partition(']:')
        return host[1:], int(port)
    host, port = hostport.rsplit(':', 1)
    return host, int(port)


def extractHost(proxy_str):
    """ proxy_str completo (con o sin auth) -> solo el host, IPv6-safe """
    host, _port = splitHostPort(stripAuth(proxy_str))
    return host
