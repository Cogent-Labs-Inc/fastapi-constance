from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_constance.models import ConstanceConfig
from fastapi_constance.utils import sync_app_settings
from fastapi_constance.wrapper import ConstanceConfigWrapper

constance_config = ConstanceConfigWrapper()


@asynccontextmanager
async def lifespan(app: FastAPI, session: AsyncSession, user_config: dict):
    """
    Async lifespan context manager for FastAPI.

    This function initializes the ConstanceConfig table in the database
    and sets up the configuration manager for dynamic app settings.
    """

    async with session.bind.begin() as conn:
        await conn.run_sync(ConstanceConfig.metadata.create_all)

    manager = await sync_app_settings(session, user_config)
    app.state.config_manager = manager
    constance_config.set_manager(manager)

    yield
