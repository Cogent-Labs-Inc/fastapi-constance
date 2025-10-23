from typing import Any, Optional

from fastapi_constance.exceptions import ImproperlyConfiguredError


class ConstanceConfigWrapper:
    """
    Provides attribute-style access to configuration values.
    """

    _manager: Optional[Any] = None

    def set_manager(self, manager: Any):
        if self._manager is not None:
            raise ImproperlyConfiguredError("Manager already configured")
        self._manager = manager

    def __getattr__(self, key: str):
        if self._manager is None:
            raise ImproperlyConfiguredError("Manager not configured")

        if key not in self._manager.cache._cache:
            raise AttributeError(f"No such config key: {key}")

        return self._manager.cache.get(key)
