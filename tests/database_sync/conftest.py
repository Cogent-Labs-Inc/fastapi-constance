from unittest.mock import AsyncMock, MagicMock

import pytest

from fastapi_constance.managers.cache import ConstanceConfigCacheManager


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
