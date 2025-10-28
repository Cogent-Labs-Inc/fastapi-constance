from typing import Any

from fastapi_constance.exceptions import ImproperlyConfiguredError


class ConstanceConfigWrapper:
    """
    Async-only wrapper for configuration values.
    Must be accessed with `await constance_config.KEY`
    Works consistently across Uvicorn and Gunicorn (async workers).
    """

    _manager = None

    def set_manager(self, manager: Any):
        if self._manager is not None:
            raise ImproperlyConfiguredError("Manager already configured")
        self._manager = manager

    async def get_value(self, key: str) -> Any:
        """Get a value from the cache."""

        if self._manager is None:
            raise ImproperlyConfiguredError("Manager not configured")

        data = self._manager.config.get(key)
        if not data:
            raise KeyError(f"{key} is not a valid config key")

        cached = await self._manager.cache.get(key)
        return self._manager.cache.type_cast_value(cached, data.get("type", str))

    async def set_value(self, key: str, value):
        """Set a value from the cache."""

        if self._manager is None:
            raise ImproperlyConfiguredError("Manager not configured")
        await self._manager.cache.set(key, value)

    def __getattr__(self, key: str):
        async def getter():
            return await self.get_value(key)

        return getter()
