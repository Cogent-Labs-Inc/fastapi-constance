from typing import Optional, Any
from .exceptions import ImproperlyConfiguredError

class ConstanceConfigWrapper:
    _manager: Optional[Any] = None

    def set_manager(self, manager: Any) -> None:
        if self._manager is not None:
            raise ImproperlyConfiguredError("Manager already configured")
        self._manager = manager

    def __getattr__(self, key: str):
        if self._manager is None:
            raise ImproperlyConfiguredError("Manager not configured")
        if key not in self._manager._config_cache:
            raise AttributeError(f"No such config key: {key}")
        return self._manager._config_cache[key]

constance_config = ConstanceConfigWrapper()
