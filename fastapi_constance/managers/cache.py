# fastapi_constance/managers/cache.py
from typing import Any, Dict

from fastapi_constance.client.redis import RedisClient
from fastapi_constance.exceptions import TypeMismatchError


class ConstanceConfigCacheManager:
    """
    Redis-backed cache with a local in-memory copy for synchronous access.

    - Reads from local memory are synchronous.
    - Writes update both Redis and local memory.
    - Type casting is supported.
    """

    def __init__(self):
        self.redis = RedisClient.get_client()
        self._local_cache: Dict[str, Any] = {}

    async def get(self, key: str) -> Any:
        """Async get from Redis"""

        value = await self.redis.get(key)
        return value

    async def set(self, key: str, value: Any):
        """Async set to Redis and update local cache"""

        if value is None:
            redis_value = "None"
        elif isinstance(value, bool):
            redis_value = "True" if value else "False"
        else:
            redis_value = str(value)

        await self.redis.set(key, redis_value)
        self._local_cache[key] = value  # store original type in memory

    async def remove(self, key: str):
        """Async remove from Redis and local cache"""

        await self.redis.delete(key)
        self._local_cache.pop(key, None)

    async def populate(self, config: Dict[str, dict]):
        """Populate Redis and local cache with default config values."""

        for key, data in config.items():
            value_type = data.get("type", str)
            value = data["value"]
            casted_value = self.type_cast_value(value, value_type)
            await self.set(key, casted_value)

    def get_sync(self, key: str) -> Any:
        """Get value synchronously from local memory"""

        if key not in self._local_cache:
            raise KeyError(f"No such config key: {key}")
        return self._local_cache[key]

    def type_cast_value(self, value: Any, value_type: type) -> Any:
        if value is None:
            return None

        if value_type is bool:
            return self._cast_to_bool(value)

        try:
            return value_type(value)
        except (ValueError, TypeError):
            raise TypeMismatchError(f"Cannot type cast value '{value}' to {value_type.__name__}")

    def _cast_to_bool(self, value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            val = value.lower()
            if val == "true":
                return True
            elif val == "false":
                return False
        raise TypeMismatchError(f"Cannot cast '{value}' to bool")
