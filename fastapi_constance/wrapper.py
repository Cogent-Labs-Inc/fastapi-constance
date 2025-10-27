import asyncio
from typing import Any, Optional

from fastapi_constance.exceptions import ImproperlyConfiguredError


class ConstanceConfigWrapper:
    """
    Synchronous wrapper for configuration values.
    Reads from the local memory cache for immediate access.
    """

    _manager: Optional[Any] = None

    def set_manager(self, manager: Any):
        self._manager = manager

    def get_value(self, key: str) -> Any:
        if self._manager is None:
            raise ImproperlyConfiguredError("Manager not configured")
        return self._manager.cache.get_sync(key)

    def set_value(self, key: str, value: Any):
        if self._manager is None:
            raise ImproperlyConfiguredError("Manager not configured")
        self._manager.cache._local_cache[key] = value
        asyncio.create_task(self._manager.cache.set(key, value))

    def __getattr__(self, key: str) -> Any:
        return self.get_value(key)
