from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_constance.admin import ConstanceConfigAdmin
from fastapi_constance.manager import ConstanceConfigManager


async def sync_app_settings(
    database_session: AsyncSession, config: dict
) -> ConstanceConfigManager:
    manager = ConstanceConfigManager(database_session, config)
    await manager.load_cache()
    return manager


def register_constance_admin(admin, user_config=None):
    """
    Register the ConstanceConfigAdmin view into an existing Admin instance.
    """

    ConstanceConfigAdmin.CONFIG = user_config or {}
    admin.add_view(ConstanceConfigAdmin)
