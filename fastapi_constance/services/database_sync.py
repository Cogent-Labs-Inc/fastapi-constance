from sqlalchemy.future import select

from fastapi_constance.exceptions import TypeMismatchError
from fastapi_constance.models import ConstanceConfig


class ConstanceConfigDatabaseSyncService:
    """Handles database synchronization for configuration entries (no cache)."""

    def __init__(self, database_session):
        self.database_session = database_session

    async def sync(self, config: dict):
        """Sync database entries with the given config."""
        result = await self.database_session.execute(select(ConstanceConfig))
        db_configs = {scalar.key: scalar for scalar in result.scalars().all()}

        for key, data in config.items():
            value = data["value"]
            desc = data.get("description")
            db_conf = db_configs.get(key)

            if db_conf:
                await self._update_existing(db_conf, value, desc)
            else:
                await self._create_new(key, value, desc)

        await self._remove_stale(config, db_configs)
        await self.database_session.commit()

    async def get_value(self, key: str, value_type: type):
        """Fetch a single configuration value directly from the database."""
        result = await self.database_session.execute(select(ConstanceConfig).where(ConstanceConfig.key == key))
        conf = result.scalar_one_or_none()
        if conf is None:
            raise KeyError(f"No configuration found for key '{key}'")

        return self._type_cast_value(conf.value, value_type)

    async def set_value(self, key: str, value, default_value, description=None):
        """Set or update a configuration value in the database."""
        if not isinstance(value, type(default_value)):
            raise TypeMismatchError(
                f"Expected {type(default_value).__name__} for key '{key}', got {type(value).__name__}"
            )

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

    async def _update_existing(self, db_conf, value, description):
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

    async def _create_new(self, key, value, description):
        new_conf = ConstanceConfig(
            key=key,
            value=str(value),
            default_value=str(value),
            description=description,
            is_admin_modified=False,
        )
        self.database_session.add(new_conf)

    async def _remove_stale(self, config, db_configs):
        for key, db_conf in db_configs.items():
            if key not in config:
                await self.database_session.delete(db_conf)

    def _type_cast_value(self, value: str, value_type: type):
        """Convert stored string values into their declared Python types."""

        if value is None:
            return None
        if value_type is bool:
            if value == "True":
                return True
            if value == "False":
                return False
            raise TypeMismatchError(f"Cannot cast '{value}' to bool.")
        try:
            return value_type(value)
        except Exception:
            raise TypeMismatchError(f"Cannot cast '{value}' to {value_type.__name__}")
