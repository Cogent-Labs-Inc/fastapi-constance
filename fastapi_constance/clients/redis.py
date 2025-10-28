import os
from typing import Optional

import redis.asyncio as redis


class RedisClient:
    """
    Async Redis client.
    Reads url/db from environment variables.
    """

    _instance: Optional[redis.Redis] = None

    @classmethod
    def get_client(cls) -> redis.Redis:
        if cls._instance is None:
            redis_url = os.getenv("REDIS_URL")
            redis_db = int(os.getenv("REDIS_DB"))

            cls._instance = redis.Redis.from_url(
                redis_url,
                decode_responses=True,
                db=redis_db,
            )
        return cls._instance
