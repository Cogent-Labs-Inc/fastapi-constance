from typing import Any, Dict

from fastapi_constance.managers.cache import ConstanceConfigCacheManager
from fastapi_constance.services.database_sync import ConstanceConfigDatabaseSyncService
from fastapi_constance.validators.constance_config import ConstanceConfigValidator


class ConstanceConfigManager:
    """
    Pure Facade for dynamic app configuration.

    Provides a simple interface to validate configuration,
    sync it with the database, and cache values for quick access.
    Delegates specific tasks to a validator, a cache manager, and a database sync service.
    """

    def __init__(self, database_session, config: Dict[str, dict]):
        self.config = config
        self.validator = ConstanceConfigValidator()
        self.cache = ConstanceConfigCacheManager()  # auto uses RedisClient with env vars
        self.database_sync = ConstanceConfigDatabaseSyncService(database_session)

    async def initialize_config_system(self):
        """Validate config, sync DB without overwriting admin-modified values, populate cache."""

        self.validator.validate_config(self.config)
        await self.database_sync.sync(self.config, self.cache)

        result = await self.database_sync.load_all()
        for db_conf in result:
            value_type = self.config.get(db_conf.key, {}).get("type", str)
            await self.cache.set(db_conf.key, self.cache.type_cast_value(db_conf.value, value_type))

    async def get(self, key: str):
        """Get a value from cache, type-casted to its original type."""

        data = self.config.get(key)
        if not data:
            raise KeyError(f"{key} is not a valid config key")
        cached = await self.cache.get(key)
        return self.cache.type_cast_value(cached, data.get("type", str))

    async def set(self, key: str, value: Any, description=None):
        """Set a config value in database and cache."""

        data = self.config.get(key)
        if not data:
            raise KeyError(f"{key} is not a valid config key")
        await self.database_sync.set_value(key, value, data["value"], self.cache, description)
