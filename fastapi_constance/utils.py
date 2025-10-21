from sqladmin import Admin
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_constance.admin import ConstanceConfigAdmin
from fastapi_constance.manager import ConstanceConfigManager


async def sync_app_settings(
    database_session: AsyncSession, config: dict
) -> ConstanceConfigManager:
    manager = ConstanceConfigManager(database_session, config)
    await manager.load_cache()
    return manager


def register_admin(app, engine, authentication_backend=None):
    admin = Admin(app, engine, authentication_backend=authentication_backend)
    admin.add_view(ConstanceConfigAdmin)
    return admin
