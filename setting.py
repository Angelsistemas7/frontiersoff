# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     setting.py
   Description :   配置文件
   Author :        JHao
   date：          2019/2/15
-------------------------------------------------
   Change Activity:
                   2019/2/15:
-------------------------------------------------
"""

BANNER = r"""
****************************************************************
*** ______  ********************* ______ *********** _  ********
*** | ___ \_ ******************** | ___ \ ********* | | ********
*** | |_/ / \__ __   __  _ __   _ | |_/ /___ * ___  | | ********
*** |  __/|  _// _ \ \ \/ /| | | ||  __// _ \ / _ \ | | ********
*** | |   | | | (_) | >  < \ |_| || |  | (_) | (_) || |___  ****
*** \_|   |_|  \___/ /_/\_\ \__  |\_|   \___/ \___/ \_____/ ****
****                       __ / /                          *****
************************* /___ / *******************************
*************************       ********************************
****************************************************************
"""

VERSION = "2.4.0"

# ############### server config ###############
HOST = "0.0.0.0"

PORT = 5010

# ############### api authentication #################
# Si se define (via variable de entorno API_KEY, nunca acá en el codigo),
# todas las rutas salvo "/" exigen el header "X-API-Key: <key>" (o
# "Authorization: Bearer <key>" para clientes que no puedan mandar headers
# custom, como Prometheus). Vacio = sin autenticacion (comportamiento
# historico, no recomendado si el puerto es alcanzable por otros).
API_KEY = ""

# ############### database config ###################
# db connection uri
# example:
#      Redis: redis://:password@ip:port/db
#      Ssdb:  ssdb://:password@ip:port
DB_CONN = 'redis://:pwdstring@127.0.0.1:6390/0'

# proxy table name
TABLE_NAME = 'use_proxy'


# ###### config the proxy fetch function ######
# 自动扫描 fetcher/sources/ 目录，加载所有 enabled=True 的 fetcher
# 如需临时禁用某个 fetcher，在下方黑名单中添加类名（不改源文件）
PROXY_FETCHER_EXCLUDE = []

# limite duro (segundos) para esperar a un hilo de fetcher individual antes
# de seguir sin el. Los fetchers ya tienen su propio timeout de red interno
# (5-10s x reintentos), pero eso no cubre stalls a nivel DNS/TCP que
# requests a veces no respeta - un solo hilo colgado bloqueaba el ciclo
# entero (visto en produccion). 60s da margen de sobra a un fetcher lento
# de verdad sin dejar que uno roto tumbe todo el pool.
FETCH_THREAD_JOIN_TIMEOUT = 60

# ############# proxy validator #################
# 代理验证目标网站
HTTP_URL = "http://httpbin.org"

HTTPS_URL = "https://www.qq.com"

# 代理验证时超时时间
VERIFY_TIMEOUT = 10

# hilos concurrentes para validar candidatos. Es trabajo de red (espera
# respuestas), no de CPU, asi que mas hilos ayuda de verdad - medido en
# vivo: ~3 candidatos/seg con 20 hilos. Se sube el default para que
# entornos con mucho volumen (Actions con 24+ fuentes) terminen mas rapido.
CHECK_THREAD_COUNT = 40

# limite duro (segundos) para esperar a un hilo de validacion antes de
# seguir sin el, mismo motivo que FETCH_THREAD_JOIN_TIMEOUT: aunque cada
# chequeo individual ya tiene su propio timeout de red, es una red de
# seguridad extra contra un stall que ningun timeout interno cubra.
CHECK_THREAD_JOIN_TIMEOUT = 120

# 近PROXY_CHECK_COUNT次校验中允许的最大失败次数,超过则剔除代理
MAX_FAIL_COUNT = 0

# 近PROXY_CHECK_COUNT次校验中允许的最大失败率,超过则剔除代理
# MAX_FAIL_RATE = 0.1

# proxyCheck时代理数量少于POOL_SIZE_MIN触发抓取
POOL_SIZE_MIN = 20

# ############# proxy attributes #################
# 是否启用代理地域属性
PROXY_REGION = True

# ############# scheduler config #################

# Set the timezone for the scheduler forcely (optional)
# If it is running on a VM, and
#   "ValueError: Timezone offset does not match system offset"
#   was raised during scheduling.
# Please uncomment the following line and set a timezone for the scheduler.
# Otherwise it will detect the timezone from the system automatically.

TIMEZONE = "Asia/Shanghai"

# ############# malicious proxy detection #################
# URLs de referencia (canary) usadas para comparar "directo" vs "a través del
# proxy". Se elige una al azar de cada lista en CADA chequeo (en vez de
# pegarle siempre al mismo dominio) para que un proxy malicioso "selectivo"
# no pueda simplemente portarse bien con el unico dominio de testing
# conocido (ej. example.com es EL clasico) y manipular todo lo demas.
MALICIOUS_CANARY_HTTP_URLS = [
    "http://example.com/",
    "http://info.cern.ch/",
    "http://neverssl.com/",
]
MALICIOUS_CANARY_HTTPS_URLS = [
    "https://example.com/",
    "https://www.cloudflare.com/",
    "https://www.google.com/",
]
MALICIOUS_CANARY_ECHO_URLS = [
    "http://httpbin.org/get",
    "http://postman-echo.com/get",
]

# risk_score >= este umbral -> cuarentena (se saca de /get pero NO se descarta ni se reporta)
MALICIOUS_QUARANTINE_THRESHOLD = 30

# risk_score >= este umbral, sostenido MALICIOUS_CONFIRM_STRIKES veces seguidas -> malicioso confirmado
MALICIOUS_CONFIRM_THRESHOLD = 60

# nro de detecciones consecutivas por encima de MALICIOUS_CONFIRM_THRESHOLD antes de
# confirmar "malicioso" y reportarlo. Evita marcar algo como malicioso por un solo falso positivo.
MALICIOUS_CONFIRM_STRIKES = 2

# ############# AbuseIPDB reporting #################
# Cuenta gratis + API key en https://www.abuseipdb.com/account/api
# Sin key configurada (via variable de entorno ABUSEIPDB_API_KEY), el reporte
# automatico simplemente se omite - no rompe nada del resto del sistema.
ABUSEIPDB_API_KEY = ""

# activa/desactiva el reporte automatico aunque haya key configurada
ABUSEIPDB_ENABLED = True

# categorias de AbuseIPDB: 9 = Open Proxy, 15 = Hacking
# https://www.abuseipdb.com/categories
ABUSEIPDB_CATEGORIES = "9,15"

# ############# lista blanca de IPs sanas #################
# nro minimo de validaciones exitosas seguidas antes de considerar un proxy "sano"
WHITELIST_MIN_CHECKS = 3

# latencia maxima (ms) para entrar en la lista blanca
WHITELIST_MAX_LATENCY_MS = 3000

# ############# viewer_safe: filtro para trafico de gente real #################
# Mas estricto que "trusted"/whitelist: pensado para cuando el proxy no lo
# usa solo tu backend (scraping, chequeos) sino gente real (ej. espectadores
# viendo un stream a traves de el). Un proxy scrapeado de fuentes publicas
# necesita muchas mas validaciones limpias seguidas Y un ancho de banda real
# medido para calificar. Los nodos propios (source "own:...") no necesitan
# cumplir el minimo de bandwidth/checks - se asume que ya confias en ellos
# por ser tuyos, pero igual deben estar "trusted" y sin ninguna señal de
# riesgo jamas registrada.
VIEWER_SAFE_MIN_CHECKS = 10

# ancho de banda minimo (kbps) para calificar - solo cuenta si se corrio
# /bandwidth/test/ en algun momento (no es automatico, ver helper/bandwidthTest.py)
VIEWER_SAFE_MIN_BANDWIDTH_KBPS = 500

# ############# nodos propios: motor gost #################
# Binario de gost (https://github.com/go-gost/gost/releases). Si no esta en
# el PATH, poner la ruta completa via variable de entorno GOST_BIN.
GOST_BIN = "gost"

# ############# medicion de ancho de banda #################
# httpbin.org/bytes/<n> devuelve n bytes aleatorios - mismo host de
# referencia ya usado en HTTP_URL/canary del detector de maliciosos.
BANDWIDTH_TEST_URL = "http://httpbin.org/bytes"

# tamano del payload de prueba (bytes). Ojo: httpbin.org/bytes/<n> tiene un
# tope silencioso de ~100KB (100_000) - pedir mas no rompe nada, pero
# httpbin devuelve como mucho eso, verificado en vivo. Se deja igual en
# 100_000 para que el numero pedido coincida con el que realmente se mide.
BANDWIDTH_TEST_SIZE_BYTES = 100_000

# timeout de la descarga de prueba (segundos) - mas alto que VERIFY_TIMEOUT
# porque acá se espera transferir datos de verdad, no solo un HEAD.
BANDWIDTH_TEST_TIMEOUT = 20

# ############# rotacion y sticky sessions #################
# TTL por defecto de una sticky session (segundos). "IP estatica" = usar un
# sticky_ttl muy largo; "rotativa" = no usar session (cada /get/ es independiente).
STICKY_DEFAULT_TTL = 1800  # 30 min

# tope maximo que se puede pedir via ?sticky_ttl= (protege contra sesiones eternas)
STICKY_MAX_TTL = 86400  # 24 horas
