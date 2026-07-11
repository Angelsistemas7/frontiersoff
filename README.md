# frontiersoff

Validador de proxies gratuitos: recolecta candidatos de fuentes públicas,
verifica que respondan de verdad, y descarta los que manipulan el tráfico
(MITM, inyección de contenido, redirecciones no pedidas).

Pensado para correr como job efímero (ver `.github/workflows/validate.yml`):
cada corrida sale con una IP propia de GitHub, hace su ciclo de validación
contra un Redis externo, y termina. No queda nada corriendo entre corridas.

## Uso

```bash
pip install -r requirements.txt
export DB_CONN="redis://:password@host:port/0"   # o rediss:// para TLS
python proxyPool.py once       # un ciclo de fetch + validacion
python proxyPool.py fetcher    # ver fuentes activas
```

## Configuración

Ver `setting.py`. Nada de credenciales va ahí — se pasan por variables de
entorno (`DB_CONN`, `ABUSEIPDB_API_KEY` opcional).
