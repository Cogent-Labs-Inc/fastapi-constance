import os
import ssl
from typing import Optional

import redis.asyncio as redis


class RedisClient:
    """
    Async Redis client.
    Reads url/db from environment variables.
    Supports TLS (e.g. rediss://) and optional SSL cert verification for managed Redis (AWS ElastiCache, etc.).
    """

    _instance: Optional[redis.Redis] = None

    @classmethod
    def get_client(cls) -> redis.Redis:
        if cls._instance is None:
            redis_url = os.getenv("REDIS_URL")
            redis_db = int(os.getenv("REDIS_DB", "0"))

            connection_kwargs = {
                "decode_responses": True,
                "db": redis_db,
            }

            ssl_cert_reqs = (os.getenv("REDIS_SSL_CERT_REQS") or "").strip().lower()
            if ssl_cert_reqs == "none":
                connection_kwargs["ssl_cert_reqs"] = ssl.CERT_NONE

            socket_connect_timeout = os.getenv("REDIS_SOCKET_CONNECT_TIMEOUT")
            if socket_connect_timeout is not None:
                try:
                    connection_kwargs["socket_connect_timeout"] = int(socket_connect_timeout)
                except ValueError:
                    pass

            cls._instance = redis.Redis.from_url(redis_url, **connection_kwargs)
        return cls._instance
