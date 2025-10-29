from unittest.mock import AsyncMock

import pytest

from fastapi_constance.clients.redis import RedisClient


@pytest.fixture(autouse=True)
def reset_redis_singleton():
    """
    Reset the RedisClient singleton before and after each test.

    Ensures that each test gets a fresh RedisClient instance
    and avoids singleton leakage across tests.
    """
    RedisClient._instance = None
    yield
    RedisClient._instance = None


@pytest.fixture
def mock_redis_client(monkeypatch):
    """
    Patch RedisClient.get_client() to return an AsyncMock instance.

    This avoids real Redis connections and allows asserting
    that Redis methods like `get`, `set`, and `delete` are awaited correctly.
    """
    mock_client = AsyncMock()
    monkeypatch.setattr("fastapi_constance.clients.redis.RedisClient.get_client", lambda: mock_client)
    return mock_client
