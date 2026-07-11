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

# ############# proxy validator #################
# 代理验证目标网站
HTTP_URL = "http://httpbin.org"

HTTPS_URL = "https://www.qq.com"

# 代理验证时超时时间
VERIFY_TIMEOUT = 10

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
# URLs de referencia (canary) usadas para comparar "directo" vs "a través del proxy"
MALICIOUS_CANARY_HTTP_URL = "http://example.com/"
MALICIOUS_CANARY_HTTPS_URL = "https://example.com/"
MALICIOUS_CANARY_ECHO_URL = "http://httpbin.org/get"

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

# ############# rotacion y sticky sessions #################
# TTL por defecto de una sticky session (segundos). "IP estatica" = usar un
# sticky_ttl muy largo; "rotativa" = no usar session (cada /get/ es independiente).
STICKY_DEFAULT_TTL = 1800  # 30 min

# tope maximo que se puede pedir via ?sticky_ttl= (protege contra sesiones eternas)
STICKY_MAX_TTL = 86400  # 24 horas
