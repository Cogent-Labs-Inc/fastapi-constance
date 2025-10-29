import pytest

from fastapi_constance.clients.redis import RedisClient


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset RedisClient singleton before each test."""
    RedisClient._instance = None
    yield
    RedisClient._instance = None
