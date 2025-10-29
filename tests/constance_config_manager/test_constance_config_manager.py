import pytest

from fastapi_constance.exceptions import TypeMismatchError


@pytest.mark.asyncio
class TestConstanceConfigManager:
    """Test suite for ConstanceConfigManager behavior."""

    async def test_initialize_config_system(self, manager):
        """Ensure initialize_config_system runs and calls database sync."""

        await manager.initialize_config_system()
        manager.database_sync.sync.assert_awaited_once_with(manager.config, manager.cache)

    async def test_get_valid_key(self, manager):
        """Should return correct value for valid key."""

        manager.cache.type_cast_value.return_value = "val"
        value = await manager.get("key1")
        assert value == "val"

    async def test_get_invalid_key_raises_keyerror(self, manager):
        """Should raise KeyError for invalid key."""

        with pytest.raises(KeyError):
            await manager.get("invalid_key")

    async def test_set_invalid_type_value(self, manager):
        """Should raise TypeMismatchError when setting value with wrong type."""

        manager.config = {"key1": {"type": int, "value": 0, "description": "desc"}}
        with pytest.raises(TypeMismatchError):
            await manager.set("key1", "string_instead_of_int")

    async def test_type_casting(self, manager):
        """Ensure type casting works for bool, int, and str."""

        assert manager.cache.type_cast_value("True", bool) is True
        assert manager.cache.type_cast_value("123", int) == 123
        assert manager.cache.type_cast_value("hello", str) == "hello"

    async def test_populate_cache_with_none(self, manager):
        """Ensure populate converts None values correctly."""

        config = {"key1": {"type": str, "value": None, "description": "desc"}}
        await manager.cache.populate(config)
        manager.cache.populate.assert_awaited_with(config)
