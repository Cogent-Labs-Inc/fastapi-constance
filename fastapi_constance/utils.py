from sqlalchemy.ext.asyncio import AsyncSession

from .manager import ConstanceConfigManager


async def sync_app_settings(database_session: AsyncSession, config: dict) -> ConstanceConfigManager:
    """
    Initialize a ConstanceConfigManager with the given database session and user-defined config,
    load the cache, and return the manager instance.

    Args:
        database_session (AsyncSession): The SQLAlchemy async session.
        config (dict): User-defined configuration dictionary.

    Returns:
        ConstanceConfigManager: Initialized and cache-loaded manager.
    """
    manager = ConstanceConfigManager(database_session, config)
    await manager.load_cache()
    return manager
