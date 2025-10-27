# fastapi_constance/redis_client.py
import os
from typing import Optional

import redis.asyncio as redis
from redis.exceptions import RedisError


class RedisClient:
    """
    Async Redis client singleton for Gunicorn multi-worker.
    Handles connection pooling internally.
    Reads host/port/db from environment variables for Docker compatibility.
    """

    _instance: Optional[redis.Redis] = None

    @classmethod
    def get_client(cls) -> redis.Redis:
        if cls._instance is None:
            redis_host = os.getenv("REDIS_HOST", "redis")
            redis_port = int(os.getenv("REDIS_PORT", 6379))
            redis_db = int(os.getenv("REDIS_DB", 0))

            redis_url = f"redis://{redis_host}:{redis_port}/{redis_db}"

            cls._instance = redis.Redis.from_url(
                redis_url,
                decode_responses=True,
                max_connections=20,
            )
        return cls._instance

    @classmethod
    async def close(cls):
        if cls._instance:
            await cls._instance.close()
            cls._instance = None

    @classmethod
    async def ping(cls) -> bool:
        try:
            client = cls.get_client()
            return await client.ping()
        except RedisError:
            return False
