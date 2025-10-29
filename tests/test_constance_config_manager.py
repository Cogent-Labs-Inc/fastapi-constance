from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from fastapi_constance.exceptions import TypeMismatchError
from fastapi_constance.managers.constance_config import ConstanceConfigManager


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def manager(mock_session):
    config = {
        "key1": {"type": str, "value": "val", "description": "desc1"},
        "key2": {"type": int, "value": 123, "description": "desc2"},
        "key3": {"type": bool, "value": True, "description": "desc3"},
    }

    with patch("fastapi_constance.clients.redis.RedisClient.get_client", return_value=AsyncMock()) as mock_redis:
        mgr = ConstanceConfigManager(mock_session, config)

        mgr.cache.type_cast_value = MagicMock(side_effect=lambda val, t: t(val) if val is not None else None)
        mgr.cache.set = AsyncMock()
        mgr.cache.populate = AsyncMock()

        mgr.database_sync.sync = AsyncMock()
        mgr.database_sync.load_all = AsyncMock(return_value=[])

        mgr.cache.redis_client = AsyncMock()
        mgr.cache.redis_client.get = AsyncMock(return_value="val")
        mgr.cache.redis_client.set = AsyncMock()

        return mgr


@pytest.mark.asyncio
async def test_initialize_config_system(manager):
    """Ensure initialize_config_system runs and calls database sync."""

    await manager.initialize_config_system()

    manager.database_sync.sync.assert_awaited_once_with(manager.config, manager.cache)


@pytest.mark.asyncio
async def test_get_valid_and_invalid_key(manager):
    """Test getting existing key and KeyError for invalid key."""

    manager.cache.type_cast_value.return_value = "val"
    value = await manager.get("key1")
    assert value == "val"

    with pytest.raises(KeyError):
        await manager.get("invalid_key")


@pytest.mark.asyncio
async def test_set_value_type_mismatch(manager):
    """Test type mismatch raises error."""

    manager.config = {"key1": {"type": int, "value": 0, "description": "desc"}}
    with pytest.raises(TypeMismatchError):
        await manager.set("key1", "string_instead_of_int")


@pytest.mark.asyncio
async def test_type_casting(manager):
    """Test type casting works for bool, int, str."""

    assert manager.cache.type_cast_value("True", bool) is True
    assert manager.cache.type_cast_value("123", int) == 123
    assert manager.cache.type_cast_value("hello", str) == "hello"


@pytest.mark.asyncio
async def test_populate_cache_with_none(manager):
    """Test that None values are converted to None string in cache."""

    config = {"key1": {"type": str, "value": None, "description": "desc"}}
    await manager.cache.populate(config)
    manager.cache.populate.assert_awaited_with(config)
