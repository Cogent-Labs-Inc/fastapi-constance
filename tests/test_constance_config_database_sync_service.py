from unittest.mock import AsyncMock, MagicMock

import pytest

from fastapi_constance.managers.cache import ConstanceConfigCacheManager
from fastapi_constance.services.database_sync import ConstanceConfigDatabaseSyncService


@pytest.fixture
def mock_cache():
    """
    Fixture that provides a mocked cache manager.

    This avoids any real Redis operations by returning an AsyncMock
    version of ConstanceConfigCacheManager with async methods for:
        - set()
        - get()
        - remove()
    """

    mock_cache_instance = AsyncMock(spec=ConstanceConfigCacheManager)
    mock_cache_instance.set = AsyncMock()
    mock_cache_instance.get = AsyncMock()
    mock_cache_instance.remove = AsyncMock()
    return mock_cache_instance


@pytest.fixture
def mock_db_session():
    """
    Fixture that provides a mocked database session.

    This simulates an asynchronous SQLAlchemy session to prevent real DB operations.
    The session includes async-compatible methods and a mock query result.
    """

    mock_session = MagicMock()

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []

    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()
    mock_session.merge = AsyncMock(return_value=None)
    mock_session.add = MagicMock()
    mock_session.delete = AsyncMock()

    return mock_session


@pytest.mark.asyncio
async def test_sync_calls_cache_set(mock_cache, mock_db_session):
    """
    Test that `sync()` correctly sets configuration values in the cache.

    Ensures that for each key-value pair in the configuration dictionary,
    the cache.set() method is awaited with the expected arguments.
    """

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
    """
    Test that `sync()` does not attempt to set any values when the config is empty.

    Ensures no unnecessary cache operations occur when an empty dictionary
    is passed to the sync method.
    """

    service = ConstanceConfigDatabaseSyncService(database_session=mock_db_session)
    await service.sync(config={}, cache=mock_cache)

    mock_cache.set.assert_not_awaited()


@pytest.mark.asyncio
async def test_sync_type_casting(mock_cache, mock_db_session):
    """
    Test that `sync()` handles type casting correctly before storing values in the cache.

    Although type casting is internal, this test verifies that the correct
    keys and values are passed to cache.set(), maintaining expected behavior.
    """

    service = ConstanceConfigDatabaseSyncService(database_session=mock_db_session)
    config = {
        "ENABLED": {"value": "False", "type": bool},
        "RETRIES": {"value": "3", "type": int},
    }

    await service.sync(config=config, cache=mock_cache)

    mock_cache.set.assert_any_await("ENABLED", "False")
    mock_cache.set.assert_any_await("RETRIES", "3")
