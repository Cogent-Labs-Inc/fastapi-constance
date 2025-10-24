from typing import Any, Optional

from fastapi_constance.exceptions import ImproperlyConfiguredError


class ConstanceConfigWrapper:
    """
    Provides attribute-style access to configuration values
    and safe public methods for cache updates.
    """

    _manager: Optional[Any] = None

    def set_manager(self, manager: Any):
        if self._manager is not None:
            raise ImproperlyConfiguredError("Manager already configured")
        self._manager = manager

    def get_value(self, key: str) -> Any:
        """Get a value from the cache."""

        if self._manager is None:
            raise ImproperlyConfiguredError("Manager not configured")
        if key not in self._manager.cache._cache:
            raise AttributeError(f"No such config key: {key}")
        return self._manager.cache.get(key)

    def set_value(self, key: str, value: Any, value_type: Optional[type] = None):
        """
        Set a value in the cache, with optional type casting.
        """

        if self._manager is None:
            raise ImproperlyConfiguredError("Manager not configured")
        if value_type:
            value = self._manager.cache.type_cast_value(value, value_type)
        self._manager.cache.set(key, value)

    def __getattr__(self, key: str) -> Any:
        return self.get_value(key)
