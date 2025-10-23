from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_constance.admin import ConstanceConfigAdmin
from fastapi_constance.manager import ConstanceConfigManager


async def sync_app_settings(database_session: AsyncSession, config: dict):
    """
    Initialize and load the application configuration cache.
    """

    manager = ConstanceConfigManager(database_session, config)
    await manager.load_cache()
    return manager


def register_constance_admin(admin, user_config: dict):
    """
    Register the ConstanceConfigAdmin view into an existing Admin instance.
    """

    ConstanceConfigAdmin.CONFIG = user_config
    admin.add_view(ConstanceConfigAdmin)
