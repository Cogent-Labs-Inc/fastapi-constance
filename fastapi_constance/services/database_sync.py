from sqlalchemy.future import select

from fastapi_constance.exceptions import TypeMismatchError
from fastapi_constance.managers.cache import ConstanceConfigCacheManager
from fastapi_constance.models import ConstanceConfig


class ConstanceConfigDatabaseSyncService:
    """Handles database sync for configuration entries."""

    def __init__(self, database_session):
        self.database_session = database_session

    async def load_all(self):
        """Return all config entries from the database."""

        result = await self.database_session.execute(select(ConstanceConfig))
        return result.scalars().all()

    async def sync(self, config: dict, cache: ConstanceConfigCacheManager):
        """
        Sync database entries with the given config and update the cache.
        """

        result = await self.database_session.execute(select(ConstanceConfig))
        db_configs = {scalar.key: scalar for scalar in result.scalars().all()}

        for key, data in config.items():
            value = data["value"]
            desc = data.get("description")
            db_conf = db_configs.get(key)

            if db_conf:
                await self._update_existing(db_conf, value, desc, cache)
            else:
                await self._create_new(key, value, desc, cache)

        await self._remove_stale(config, db_configs, cache)
        await self.database_session.commit()

    async def set_config(self, key: str, value, default_value, description=None):
        """
        Create or update a config entry in the database.
        """

        conf = ConstanceConfig(
            key=key,
            value=str(value),
            default_value=str(default_value),
            description=description,
            is_admin_modified=True,
        )
        db_conf = await self.database_session.merge(conf)
        await self.database_session.commit()
        return db_conf

    async def _update_existing(self, db_conf, value, description, cache):
        """
        Update an existing config record and refresh the cache.
        If the value was modified by admin, never override it with defaults.
        """

        updated = False

        if description and db_conf.description != description:
            db_conf.description = description
            updated = True

        if not db_conf.is_admin_modified:
            if db_conf.value != str(value):
                db_conf.value = str(value)
                db_conf.default_value = str(value)
                updated = True
        else:
            if db_conf.default_value != str(value):
                db_conf.default_value = str(value)
                updated = True

        if updated:
            self.database_session.add(db_conf)

        await cache.set(db_conf.key, cache.type_cast_value(db_conf.value, type(value)))

    async def _create_new(self, key, value, description, cache: ConstanceConfigCacheManager):
        """
        Create a new config record and add it to the cache.
        """

        new_conf = ConstanceConfig(
            key=key,
            value=str(value),
            default_value=str(value),
            description=description,
            is_admin_modified=False,
        )
        self.database_session.add(new_conf)

        await cache.set(key, value)

    async def _remove_stale(self, config, db_configs, cache: ConstanceConfigCacheManager):
        """
        Remove database configs that are not in the provided config dictionary.
        """

        to_remove = []

        for key, db_conf in db_configs.items():
            if key not in config:
                await self.database_session.delete(db_conf)
                to_remove.append(key)

        for key in to_remove:
            await cache.remove(key)

    async def set_value(self, key: str, value, default_value, cache: ConstanceConfigCacheManager, description=None):
        """
        Set a configuration value in the database and update the cache.
        """

        if not isinstance(value, type(default_value)):
            raise TypeMismatchError(
                f"Expected {type(default_value).__name__} for key '{key}', got {type(value).__name__}"
            )

        await self.set_config(key, value, default_value, description)
        await cache.set(key, value)
