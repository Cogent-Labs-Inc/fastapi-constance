from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_constance.admin import ConstanceConfigAdmin
from fastapi_constance.managers.constance_config import ConstanceConfigManager
from fastapi_constance.models import ConstanceConfig


async def sync_app_settings(database_session: AsyncSession, config: dict):
    """
    Initialize and load the application configuration cache.
    """

    manager = ConstanceConfigManager(database_session, config)
    await manager.initialize_config_system()

    return manager


def create_constance_table(connection):
    """
    Create only the ConstanceConfig table.
    """

    ConstanceConfig.__table__.create(connection, checkfirst=True)


def register_constance_admin(admin, user_config: dict):
    """
    Register the ConstanceConfigAdmin view into an existing Admin instance.
    """

    ConstanceConfigAdmin.CONFIG = user_config
    admin.add_view(ConstanceConfigAdmin)
