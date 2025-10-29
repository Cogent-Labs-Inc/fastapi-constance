from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from fastapi_constance.managers.constance_config import ConstanceConfigManager


@pytest.fixture
def mock_session():
    """Provide a mocked async session."""

    return AsyncMock()


@pytest.fixture
def manager(mock_session):
    """Fixture that returns a configured ConstanceConfigManager instance with mocks."""

    config = {
        "key1": {"type": str, "value": "val", "description": "desc1"},
        "key2": {"type": int, "value": 123, "description": "desc2"},
        "key3": {"type": bool, "value": True, "description": "desc3"},
    }

    with patch("fastapi_constance.clients.redis.RedisClient.get_client", return_value=AsyncMock()):
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
