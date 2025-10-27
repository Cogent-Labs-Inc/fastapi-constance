from fastapi_constance.services.database_sync import ConstanceConfigDatabaseSyncService
from fastapi_constance.validators.constance_config import ConstanceConfigValidator


class ConstanceConfigManager:
    """
    Pure Facade for dynamic app configuration — database-only version.

    Provides a simple interface to validate configuration,
    sync it with the database, and retrieve/update values directly.
    """

    def __init__(self, database_session, config: dict):
        self.config = config
        self.validator = ConstanceConfigValidator()
        self.database_sync = ConstanceConfigDatabaseSyncService(database_session)

    async def initialize_config_system(self):
        """Validate config and sync with database."""

        self.validator.validate_config(self.config)
        await self.database_sync.sync(self.config)

    async def get(self, key: str):
        """Get a value directly from the database."""

        data = self.config.get(key)
        if not data:
            raise KeyError(f"{key} is not a valid config key")
        return await self.database_sync.get_value(key, data.get("type", str))

    async def set(self, key: str, value, description=None):
        """Set a config value in database."""

        data = self.config.get(key)
        if not data:
            raise KeyError(f"{key} is not a valid config key")
        await self.database_sync.set_value(key, value, data["value"], description)
