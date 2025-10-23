from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from fastapi_constance.exceptions import (NotSupportedTypeError,
                                          TypeMismatchError)
from fastapi_constance.managers.cache import ConstanceCache
from fastapi_constance.models import ConstanceConfig


class ConstanceConfigManager:
    """
    Manages dynamic configuration similar to Django Constance.
    """

    SUPPORTED_TYPES = (int, float, str, bool)

    def __init__(self, database_session: AsyncSession, config: Dict[str, dict]):
        """
        Initialize the configuration manager with a database session and user-defined config.
        """

        self.database_session = database_session
        self.config = config
        self.cache = ConstanceCache()

    async def load_cache(self):
        """
        Validate configuration, synchronize database entries, and populate the cache.
        """

        self._validate_config()
        await self._sync_database_with_config()
        self.cache.populate(self.config)

    def _validate_config(self):
        """
        Validate structure and type correctness of configuration entries.
        """

        self._validate_required_keys()
        self._validate_types()

    def _validate_required_keys(self):
        """
        Ensure each configuration entry includes required keys.
        """

        required_keys = ["value", "description", "type"]
        for key, data in self.config.items():
            for rk in required_keys:
                if rk not in data:
                    raise KeyError(f"Missing '{rk}' for key '{key}' in config")

    def _validate_types(self):
        """
        Validate that all configuration values match their declared types.
        """

        for key, data in self.config.items():
            value, value_type = data["value"], data.get("type")
            if value_type not in self.SUPPORTED_TYPES:
                raise NotSupportedTypeError(
                    f"Type {value_type.__name__} not supported for key '{key}'"
                )
            if not isinstance(value, value_type):
                raise TypeMismatchError(
                    f"Default value for '{key}' must be of type {value_type.__name__}, "
                    f"got {type(value).__name__}"
                )

    async def _sync_database_with_config(self):
        """
        Synchronize database entries with the provided configuration.
        """

        result = await self.database_session.execute(select(ConstanceConfig))
        database_configs = {conf.key: conf for conf in result.scalars().all()}

        for key, data in self.config.items():
            default_value = data["value"]
            desc = data.get("description")
            db_conf = database_configs.get(key)

            if db_conf:
                await self._update_existing_config(db_conf, default_value, desc)
            else:
                await self._create_new_config(key, default_value, desc)

        await self._remove_stale_database_configs(database_configs)

    async def _remove_stale_database_configs(self, database_configs: dict):
        """
        Remove configurations from the database that are not defined in the user config.
        """

        for key, db_conf in database_configs.items():
            if key not in self.config:
                await self.database_session.delete(db_conf)
                await self.database_session.commit()
                self.cache.remove(key)

    async def _update_existing_config(self, db_conf, default_value, default_desc):
        """
        Update an existing configuration in the database and cache.
        """

        value_type = type(default_value)
        type_casted_value = self.cache.type_cast_value(db_conf.value, value_type)

        updated = False

        if db_conf.description != default_desc:
            db_conf.description = default_desc
            updated = True

        if not db_conf.is_admin_modified:
            if db_conf.default_value != str(default_value) or db_conf.value != str(
                default_value
            ):
                db_conf.default_value = db_conf.value = str(default_value)
                updated = True
        elif db_conf.default_value != str(default_value):
            db_conf.default_value = str(default_value)
            updated = True

        if updated:
            self.database_session.add(db_conf)
            await self.database_session.commit()

        self.cache.set(db_conf.key, type_casted_value)

    async def _create_new_config(self, key, default_value, default_desc):
        """
        Create a new configuration record in the database and add it to the cache.
        """

        new_conf = ConstanceConfig(
            key=key,
            value=str(default_value),
            default_value=str(default_value),
            description=default_desc,
            is_admin_modified=False,
        )
        self.database_session.add(new_conf)
        await self.database_session.commit()
        self.cache.set(key, default_value)

    async def get(self, key: str):
        """
        Retrieve a configuration value from the cache, type-casted to its declared type.
        """

        data = self.config.get(key)
        if not data:
            raise KeyError(f"{key} is not a valid config key")

        value_type = data.get("type", str)
        cached_value = self.cache.get(key)
        return self.cache.type_cast_value(cached_value, value_type)

    async def set(self, key: str, value: Any, description: Optional[str] = None):
        """
        Update or create a configuration entry in the database and cache.
        """

        data = self.config.get(key)
        if not data:
            raise KeyError(f"{key} is not a valid config key")

        value_type = data.get("type", str)
        if not isinstance(value, value_type):
            raise TypeMismatchError(
                f"Expected {value_type.__name__} for key '{key}', got {type(value).__name__}"
            )

        db_conf = await self.database_session.get(ConstanceConfig, key)
        if db_conf:
            db_conf.value = str(value)
            db_conf.is_admin_modified = True
            if description:
                db_conf.description = description
            self.database_session.add(db_conf)
        else:
            new_conf = ConstanceConfig(
                key=key,
                value=str(value),
                default_value=str(data["value"]),
                description=description,
                is_admin_modified=True,
            )
            self.database_session.add(new_conf)

        await self.database_session.commit()
        self.cache.set(key, value)
