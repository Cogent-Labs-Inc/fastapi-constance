from sqlalchemy.future import select

from fastapi_constance.exceptions import TypeMismatchError
from fastapi_constance.managers.cache import ConstanceConfigCacheManager
from fastapi_constance.models import ConstanceConfig


class ConstanceConfigDatabaseSyncService:
    """Handles database sync for configuration entries."""

    def __init__(self, database_session):
        self.database_session = database_session

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

    async def get_config(self, key: str):
        """
        Retrieve a config entry from the database by key.
        """

        return await self.database_session.get(ConstanceConfig, key)

    async def set_config(self, key: str, value, default_value, description=None):
        """
        Create or update a config entry in the database.
        """

        db_conf = await self.get_config(key)
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
                default_value=str(default_value),
                description=description,
                is_admin_modified=True,
            )
            self.database_session.add(new_conf)

        await self.database_session.commit()
        return db_conf or new_conf

    async def _update_existing(
        self, db_conf, value, description, cache: ConstanceConfigCacheManager
    ):
        """
        Update an existing config record and refresh the cache.
        """

        updated = False

        if db_conf.description != description:
            db_conf.description = description
            updated = True

        if not db_conf.is_admin_modified:
            if db_conf.default_value != str(value) or db_conf.value != str(value):
                db_conf.default_value = db_conf.value = str(value)
                updated = True
        elif db_conf.default_value != str(value):
            db_conf.default_value = str(value)
            updated = True

        if updated:
            self.database_session.add(db_conf)
            await self.database_session.commit()

        cache.set(db_conf.key, cache.type_cast_value(db_conf.value, type(value)))

    async def _create_new(
        self, key, value, description, cache: ConstanceConfigCacheManager
    ):
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
        await self.database_session.commit()
        cache.set(key, value)

    async def _remove_stale(
        self, config, db_configs, cache: ConstanceConfigCacheManager
    ):
        """
        Remove database configs that are not in the provided config dictionary.
        """

        for key, db_conf in db_configs.items():
            if key not in config:
                await self.database_session.delete(db_conf)
                await self.database_session.commit()
                cache.remove(key)

    async def set_value(self, key: str, value, default_value, cache, description=None):
        if not isinstance(value, type(default_value)):
            raise TypeMismatchError(
                f"Expected {type(default_value).__name__} for key '{key}', got {type(value).__name__}"
            )

        await self.set_config(key, value, default_value, description)
        cache.set(key, value)
