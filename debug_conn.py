import os
import redis

uri = os.environ["DB_CONN"]
print("scheme:", uri.split("://")[0])
r = redis.Redis.from_url(uri, decode_responses=True, socket_timeout=10, socket_connect_timeout=10)
print("PING ->", r.ping())
print("DBSIZE ->", r.dbsize())
