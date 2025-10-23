from fastapi_constance.exceptions import TypeMismatchError
from fastapi_constance.managers.cache import ConstanceConfigCacheManager
from fastapi_constance.services.database_sync import \
    ConstanceConfigDatabaseSyncService
from fastapi_constance.validators.constance_config import \
    ConstanceConfigValidator


class ConstanceConfigManager:
    """
    Pure Facade for dynamic app configuration.

    Provides a simple interface to validate configuration,
    sync it with the database, and cache values for quick access.
    Delegates specific tasks to a validator, a cache manager, and a database sync service.
    """

    def __init__(self, database_session, config: dict):
        self.config = config
        self.validator = ConstanceConfigValidator()
        self.cache = ConstanceConfigCacheManager()
        self.database_sync = ConstanceConfigDatabaseSyncService(database_session)

    async def load_cache(self):
        """Validate config, sync database, and populate cache."""

        self.validator.validate_config(self.config)
        await self.database_sync.sync(self.config, self.cache)
        self.cache.populate(self.config)

    async def get(self, key: str):
        """Get a value from cache, type-casted to its original type."""

        data = self.config.get(key)
        if not data:
            raise KeyError(f"{key} is not a valid config key")
        cached = self.cache.get(key)

        return self.cache.type_cast_value(cached, data.get("type", str))

    async def set(self, key: str, value, description=None):
        """Set a config value in database and cache."""

        data = self.config.get(key)
        if not data:
            raise KeyError(f"{key} is not a valid config key")

        value_type = data.get("type", str)
        if not isinstance(value, value_type):
            raise TypeMismatchError(
                f"Expected {value_type.__name__} for key '{key}', got {type(value).__name__}"
            )

        await self.database_sync.set_config(key, value, data["value"], description)

        self.cache.set(key, value)
