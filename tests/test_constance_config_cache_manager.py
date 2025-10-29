from unittest.mock import AsyncMock

import pytest

from fastapi_constance.clients.redis import RedisClient
from fastapi_constance.exceptions import TypeMismatchError
from fastapi_constance.managers.cache import ConstanceConfigCacheManager


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


@pytest.mark.asyncio
async def test_get_value_from_redis(mock_redis_client):
    """
    Test that `get()` retrieves a value from Redis
    and returns the expected result.
    """

    mock_redis_client.get.return_value = "value123"
    cache = ConstanceConfigCacheManager()
    result = await cache.get("test_key")
    mock_redis_client.get.assert_awaited_once_with("test_key")
    assert result == "value123"


@pytest.mark.asyncio
async def test_set_value_str(mock_redis_client):
    """
    Test that `set()` stores a string value correctly in Redis.
    """

    cache = ConstanceConfigCacheManager()
    await cache.set("test_key", "hello")
    mock_redis_client.set.assert_awaited_once_with("test_key", "hello")


@pytest.mark.asyncio
async def test_set_value_bool(mock_redis_client):
    """
    Test that `set()` correctly converts boolean values
    to their string equivalents ("True"/"False") before saving.
    """

    cache = ConstanceConfigCacheManager()
    await cache.set("bool_true", True)
    await cache.set("bool_false", False)
    mock_redis_client.set.assert_any_await("bool_true", "True")
    mock_redis_client.set.assert_any_await("bool_false", "False")


@pytest.mark.asyncio
async def test_set_value_none(mock_redis_client):
    """
    Test that `set()` converts None values to the string "None"
    before saving them to Redis.
    """

    cache = ConstanceConfigCacheManager()
    await cache.set("none_key", None)
    mock_redis_client.set.assert_awaited_once_with("none_key", "None")


@pytest.mark.asyncio
async def test_remove_key(mock_redis_client):
    """
    Test that `remove()` correctly calls Redis `delete()`
    to remove a key.
    """

    cache = ConstanceConfigCacheManager()
    await cache.remove("delete_key")
    mock_redis_client.delete.assert_awaited_once_with("delete_key")


@pytest.mark.asyncio
async def test_populate_config(mock_redis_client):
    """
    Test that `populate()` iterates over the provided config dict
    and sets each key-value pair in Redis with proper type casting.
    """

    cache = ConstanceConfigCacheManager()
    config = {
        "DEBUG": {"value": "True", "type": bool},
        "TIMEOUT": {"value": "15", "type": int},
        "APP_NAME": {"value": "constance", "type": str},
    }
    await cache.populate(config)
    mock_redis_client.set.assert_any_await("DEBUG", "True")
    mock_redis_client.set.assert_any_await("TIMEOUT", "15")
    mock_redis_client.set.assert_any_await("APP_NAME", "constance")
    assert mock_redis_client.set.await_count == 3


def test_type_cast_value_valid_types(mock_redis_client):
    """
    Test that `type_cast_value()` correctly casts valid primitive types:
    int, bool, and str.
    """

    cache = ConstanceConfigCacheManager()
    assert cache.type_cast_value("10", int) == 10
    assert cache.type_cast_value("True", bool) is True
    assert cache.type_cast_value("False", bool) is False
    assert cache.type_cast_value("sample", str) == "sample"


def test_type_cast_value_invalid_bool(mock_redis_client):
    """
    Test that invalid boolean string values raise a TypeMismatchError.
    """

    cache = ConstanceConfigCacheManager()
    with pytest.raises(TypeMismatchError):
        cache.type_cast_value("yes", bool)


def test_type_cast_value_invalid_cast(mock_redis_client):
    """
    Test that invalid type casting (e.g., "abc" → int)
    raises a TypeMismatchError.
    """

    cache = ConstanceConfigCacheManager()
    with pytest.raises(TypeMismatchError):
        cache.type_cast_value("abc", int)


def test_cast_to_bool_valid_inputs(mock_redis_client):
    """
    Test that `_cast_to_bool()` correctly handles valid inputs:
    both bool and string representations of True/False.
    """

    cache = ConstanceConfigCacheManager()
    assert cache._cast_to_bool(True) is True
    assert cache._cast_to_bool("True") is True
    assert cache._cast_to_bool("False") is False


def test_cast_to_bool_invalid_input(mock_redis_client):
    """
    Test that `_cast_to_bool()` raises TypeMismatchError for
    invalid string inputs like "yes" or "no".
    """

    cache = ConstanceConfigCacheManager()
    with pytest.raises(TypeMismatchError):
        cache._cast_to_bool("yes")
