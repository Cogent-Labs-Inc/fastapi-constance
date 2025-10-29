from unittest.mock import AsyncMock, MagicMock

import pytest

from fastapi_constance.managers.cache import ConstanceConfigCacheManager
from fastapi_constance.services.database_sync import ConstanceConfigDatabaseSyncService

# ------------------ Fixtures ------------------


@pytest.fixture
def mock_cache(monkeypatch):
    """
    Patch ConstanceConfigCacheManager to avoid real Redis calls.
    Returns a mocked AsyncMock instance with async set/remove/get methods.
    """
    mock_cache_instance = AsyncMock(spec=ConstanceConfigCacheManager)
    mock_cache_instance.set = AsyncMock()
    mock_cache_instance.get = AsyncMock()
    mock_cache_instance.remove = AsyncMock()

    monkeypatch.setattr(
        "fastapi_constance.services.database_sync.ConstanceConfigCacheManager", lambda: mock_cache_instance
    )
    return mock_cache_instance


@pytest.fixture
def mock_db_session():
    """
    Returns a mocked database session for injecting into the service.
    Makes `execute` awaitable and returns a mock result with `scalars().all()`.
    """
    mock_session = MagicMock()

    # Mock result object for execute
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []

    # Make execute awaitable
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()
    mock_session.merge = AsyncMock(return_value=None)
    mock_session.add = MagicMock()
    mock_session.delete = AsyncMock()

    return mock_session


# ------------------ Database sync service tests ------------------


@pytest.mark.asyncio
async def test_sync_calls_cache_set(mock_cache, mock_db_session):
    service = ConstanceConfigDatabaseSyncService(database_session=mock_db_session)
    config = {
        "DEBUG": {"value": "True", "type": bool},
        "TIMEOUT": {"value": "15", "type": int},
    }

    await service.sync(config=config, cache=mock_cache)

    mock_cache.set.assert_any_await("DEBUG", "True")
    mock_cache.set.assert_any_await("TIMEOUT", "15")
    assert mock_cache.set.await_count == 2


@pytest.mark.asyncio
async def test_sync_empty_config(mock_cache, mock_db_session):
    service = ConstanceConfigDatabaseSyncService(database_session=mock_db_session)
    await service.sync(config={}, cache=mock_cache)  # empty dict
    mock_cache.set.assert_not_awaited()


@pytest.mark.asyncio
async def test_sync_type_casting(mock_cache, mock_db_session):
    service = ConstanceConfigDatabaseSyncService(database_session=mock_db_session)
    config = {
        "ENABLED": {"value": "False", "type": bool},
        "RETRIES": {"value": "3", "type": int},
    }

    await service.sync(config=config, cache=mock_cache)

    mock_cache.set.assert_any_await("ENABLED", "False")
    mock_cache.set.assert_any_await("RETRIES", "3")
