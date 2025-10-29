import pytest

from fastapi_constance.exceptions import TypeMismatchError
from fastapi_constance.managers.cache import ConstanceConfigCacheManager


@pytest.mark.asyncio
class TestConstanceConfigCacheManager:
    """
    Test suite for ConstanceConfigCacheManager to ensure that
    Redis caching, type casting, and data population behaviors
    work as expected.
    """

    async def test_get_value_from_redis(self, mock_redis_client):
        """
        Test that `get()` retrieves a value from Redis
        and returns the expected result.
        """

        mock_redis_client.get.return_value = "value123"
        cache = ConstanceConfigCacheManager()
        result = await cache.get("test_key")
        mock_redis_client.get.assert_awaited_once_with("test_key")
        assert result == "value123"

    async def test_set_str_value(self, mock_redis_client):
        """
        Test that `set()` stores a string value correctly in Redis.
        """

        cache = ConstanceConfigCacheManager()
        await cache.set("test_key", "hello")
        mock_redis_client.set.assert_awaited_once_with("test_key", "hello")

    async def test_set_bool_value(self, mock_redis_client):
        """
        Test that `set()` correctly converts boolean values
        to their string equivalents ("True"/"False") before saving.
        """

        cache = ConstanceConfigCacheManager()
        await cache.set("bool_true", True)
        await cache.set("bool_false", False)
        mock_redis_client.set.assert_any_await("bool_true", "True")
        mock_redis_client.set.assert_any_await("bool_false", "False")

    async def test_set_none_value(self, mock_redis_client):
        """
        Test that `set()` converts None values to the string "None"
        before saving them to Redis.
        """

        cache = ConstanceConfigCacheManager()
        await cache.set("none_key", None)
        mock_redis_client.set.assert_awaited_once_with("none_key", "None")

    async def test_remove_key(self, mock_redis_client):
        """
        Test that `remove()` correctly calls Redis `delete()`
        to remove a key.
        """

        cache = ConstanceConfigCacheManager()
        await cache.remove("delete_key")
        mock_redis_client.delete.assert_awaited_once_with("delete_key")

    async def test_populate_config(self, mock_redis_client):
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


class TestTypeCasting:
    """
    Test suite for type casting helper methods in ConstanceConfigCacheManager.
    """

    def test_type_cast_valid_values(self, mock_redis_client):
        """
        Test that `type_cast_value()` correctly casts valid primitive types:
        int, bool, and str.
        """

        cache = ConstanceConfigCacheManager()
        assert cache.type_cast_value("10", int) == 10
        assert cache.type_cast_value("True", bool) is True
        assert cache.type_cast_value("False", bool) is False
        assert cache.type_cast_value("sample", str) == "sample"

    def test_type_cast_invalid_bool(self, mock_redis_client):
        """
        Test that invalid boolean string values raise a TypeMismatchError.
        """

        cache = ConstanceConfigCacheManager()
        with pytest.raises(TypeMismatchError):
            cache.type_cast_value("yes", bool)

    def test_type_cast_invalid_cast(self, mock_redis_client):
        """
        Test that invalid type casting (e.g., "abc" → int)
        raises a TypeMismatchError.
        """

        cache = ConstanceConfigCacheManager()
        with pytest.raises(TypeMismatchError):
            cache.type_cast_value("abc", int)

    def test_cast_to_bool_valid_inputs(self, mock_redis_client):
        """
        Test that `_cast_to_bool()` correctly handles valid inputs:
        both bool and string representations of True/False.
        """

        cache = ConstanceConfigCacheManager()
        assert cache._cast_to_bool(True) is True
        assert cache._cast_to_bool("True") is True
        assert cache._cast_to_bool("False") is False

    def test_cast_to_bool_invalid_input(self, mock_redis_client):
        """
        Test that `_cast_to_bool()` raises TypeMismatchError for
        invalid string inputs like "yes" or "no".
        """

        cache = ConstanceConfigCacheManager()
        with pytest.raises(TypeMismatchError):
            cache._cast_to_bool("yes")
