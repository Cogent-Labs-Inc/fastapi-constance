from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .config import CONFIG
from .exceptions import NotSupportedTypeError, TypeMismatchError
from .models import ConstanceConfig


class ConstanceConfigManager:
    """
    Manages dynamic configuration similar to Django Constance.
    - Supports types: int, float, str, bool.
    - Type is controlled by code only (admin cannot change it).
    - Raises instantly on reload if type or value mismatch is found.
    """

    SUPPORTED_TYPES = (int, float, str, bool)

    def __init__(self, database_session: AsyncSession):
        self.database_session = database_session
        self._config_cache: dict[str, Any] = {}

    async def load_cache(self):
        """Main entry point: validate CONFIG, sync DB, populate cache."""

        self._validate_config()
        await self._sync_database_with_config()
        await self._populate_cache()

    def _validate_config(self):
        """Validate structure and type correctness of all CONFIG items."""

        self._validate_required_keys()
        self._validate_types_and_defaults()

    def _validate_required_keys(self):
        """Ensure each CONFIG entry includes required keys."""

        required_keys = ["value", "description", "type"]

        for key, data in CONFIG.items():
            for required_key in required_keys:
                if required_key not in data:
                    raise KeyError(
                        f"Missing '{required_key}' for key '{key}' in CONFIG"
                    )

    def _validate_types_and_defaults(self):
        """Ensure CONFIG values match their declared types and supported types."""

        for key, data in CONFIG.items():
            value = data["value"]
            value_type = data.get("type")

            if value_type is None:
                raise NotSupportedTypeError(f"Missing 'type' for key '{key}' in CONFIG")

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
        """Insert, update, or delete DB entries to match CONFIG."""

        result = await self.database_session.execute(select(ConstanceConfig))
        database_configs = {scalar.key: scalar for scalar in result.scalars().all()}

        for key, data in CONFIG.items():
            default_value = data["value"]
            default_description = data.get("description")
            value_type = data.get("type", str)

            database_config = database_configs.get(key)

            if database_config:
                await self._update_existing_config(
                    database_config, default_value, default_description
                )
            else:
                await self._create_new_config(key, default_value, default_description)

        await self._remove_stale_database_configs(database_configs)

    async def _remove_stale_database_configs(self, database_configs: dict):
        """Delete configs that exist in DB but not in CONFIG."""

        for key, database_config in database_configs.items():
            if key not in CONFIG:
                await self.database_session.delete(database_config)
                await self.database_session.commit()
                self._config_cache.pop(key, None)

    async def _update_existing_config(
        self, database_config, default_value, default_description
    ):
        """Update DB record if description or default changes, respecting admin overrides."""

        try:
            type_casted_value = self._type_cast_value(
                database_config.value, type(default_value)
            )
        except (ValueError, TypeError):
            raise TypeMismatchError(
                f"Value for key '{database_config.key}' does not match type {type(default_value).__name__}"
            )

        updated = False

        if database_config.description != default_description:
            database_config.description = default_description
            updated = True

        if not database_config.is_admin_modified:
            if database_config.default_value != str(
                default_value
            ) or database_config.value != str(default_value):
                database_config.default_value = str(default_value)
                database_config.value = str(default_value)
                updated = True
        else:
            if database_config.default_value != str(default_value):
                database_config.default_value = str(default_value)
                updated = True

        if updated:
            self.database_session.add(database_config)
            await self.database_session.commit()

        self._config_cache[database_config.key] = type_casted_value

    async def _create_new_config(
        self, key: str, default_value: Any, default_description: Optional[str]
    ):
        """Insert a new config record into the DB and cache."""

        new_conf = ConstanceConfig(
            key=key,
            value=str(default_value),
            default_value=str(default_value),
            description=default_description,
            is_admin_modified=False,
        )

        self.database_session.add(new_conf)
        await self.database_session.commit()
        self._config_cache[key] = default_value

    async def _populate_cache(self):
        """Ensure cache is updated with all values from DB type-casted to correct types."""

        for key, data in CONFIG.items():
            cached_value = self._config_cache.get(key)
            value_type = data.get("type", str)
            self._config_cache[key] = self._type_cast_value(cached_value, value_type)

    async def get(self, key: str):
        """Retrieve a configuration value by key, type-casted to its declared type."""

        result = None
        data = CONFIG.get(key)

        if data:
            value_type = data.get("type", str)
            cached_value = self._config_cache.get(key)
            result = self._type_cast_value(cached_value, value_type)

        return result

    async def set(self, key: str, value: Any, description: Optional[str] = None):
        """Update or create a configuration value in both DB and cache."""

        data = CONFIG.get(key)
        if not data:
            raise KeyError(f"{key} is not a valid configuration key")

        value_type = data.get("type", str)
        if value_type not in self.SUPPORTED_TYPES:
            raise NotSupportedTypeError(f"Type {value_type.__name__} not supported")

        if not isinstance(value, value_type):
            raise TypeMismatchError(
                f"Expected {value_type.__name__} for key '{key}', got {type(value).__name__}"
            )

        database_config = await self.database_session.get(ConstanceConfig, key)

        if database_config:
            database_config.value = str(value)
            database_config.is_admin_modified = True

            if description:
                database_config.description = description

            self.database_session.add(database_config)
        else:
            new_config = ConstanceConfig(
                key=key,
                value=str(value),
                default_value=str(data["value"]),
                description=description,
                is_admin_modified=True,
            )

            self.database_session.add(new_config)

        await self.database_session.commit()
        self._config_cache[key] = value

    def _type_cast_value(self, value: Any, value_type: type):
        """Type-cast stored string value back to its declared Python type, strictly handling bool."""

        result = None

        if value is None:
            result = None

        elif value_type is bool:
            if isinstance(value, str):
                if value == "True":
                    result = True
                elif value == "False":
                    result = False
                else:
                    raise TypeMismatchError(
                        f"Cannot type cast '{value}' to bool. Must be 'True' or 'False'."
                    )
            elif isinstance(value, bool):
                result = value
            else:
                raise TypeMismatchError(
                    f"Cannot type cast '{value}' of type {type(value).__name__} to bool."
                )
        else:
            try:
                result = value_type(value)
            except (ValueError, TypeError):
                raise TypeMismatchError(
                    f"Cannot type cast value '{value}' to {value_type.__name__}"
                )

        return result
