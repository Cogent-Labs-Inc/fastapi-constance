from sqlalchemy.ext.asyncio import AsyncSession

from .manager import ConstanceConfigManager

from contextlib import asynccontextmanager
from fastapi import FastAPI
from .wrapper import constance_config
from typing import Callable, Awaitable


async def sync_app_settings(database_session: AsyncSession):
    manager = ConstanceConfigManager(database_session)
    await manager.load_cache()

    return manager


@asynccontextmanager
async def lifespan(app: FastAPI, session_factory: Callable[[], Awaitable] = None):
    """
    User provides session_factory (async session).
    """
    if session_factory is None:
        raise RuntimeError("You must provide session_factory for lifespan")

    async with session_factory() as session:
        manager = await sync_app_settings(session)
        app.state.config_manager = manager
        constance_config.set_manager(manager)
        yield
