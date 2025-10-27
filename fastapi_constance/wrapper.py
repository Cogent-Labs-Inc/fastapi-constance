import asyncio
from typing import Any, Optional

from fastapi_constance.exceptions import ImproperlyConfiguredError


class ConstanceConfigWrapper:
    """
    Provides attribute-style access to configuration values.

    ✅ Works in both async & sync contexts:
       - In async code: await constance_config.KEY
       - In sync code: constance_config.KEY
    """

    _manager: Optional[Any] = None

    def set_manager(self, manager: Any):
        """Attach the configuration manager after initialization."""
        if self._manager is not None:
            raise ImproperlyConfiguredError("Manager already configured")
        self._manager = manager

    def __getattr__(self, key: str) -> Any:
        if self._manager is None:
            raise ImproperlyConfiguredError("Manager not configured")

        async def getter():
            return await self._manager.get(key)

        try:
            asyncio.get_running_loop()
            return getter()
        except RuntimeError:
            return asyncio.run(getter())
