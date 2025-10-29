from unittest.mock import AsyncMock, MagicMock

import pytest

from fastapi_constance.exceptions import ImproperlyConfiguredError
from fastapi_constance.wrapper import ConstanceConfigWrapper


@pytest.fixture
def mock_manager():
    manager = MagicMock()
    manager.config = {"TEST_KEY": {"type": int, "value": 10}}
    manager.cache = MagicMock()
    manager.cache.get = AsyncMock(return_value="42")
    manager.cache.type_cast_value = MagicMock(return_value=42)
    manager.cache.set = AsyncMock()
    return manager


@pytest.mark.asyncio
async def test_set_manager_once(mock_manager):
    wrapper = ConstanceConfigWrapper()
    wrapper.set_manager(mock_manager)

    with pytest.raises(ImproperlyConfiguredError):
        wrapper.set_manager(mock_manager)


@pytest.mark.asyncio
async def test_get_value_success(mock_manager):
    wrapper = ConstanceConfigWrapper()
    wrapper.set_manager(mock_manager)

    value = await wrapper.get_value("TEST_KEY")
    assert value == 42
    mock_manager.cache.get.assert_awaited_with("TEST_KEY")
    mock_manager.cache.type_cast_value.assert_called_once_with("42", int)


@pytest.mark.asyncio
async def test_get_value_invalid_key(mock_manager):
    wrapper = ConstanceConfigWrapper()
    wrapper.set_manager(mock_manager)

    with pytest.raises(KeyError):
        await wrapper.get_value("INVALID_KEY")


@pytest.mark.asyncio
async def test_get_value_without_manager():
    wrapper = ConstanceConfigWrapper()
    with pytest.raises(ImproperlyConfiguredError):
        await wrapper.get_value("TEST_KEY")


@pytest.mark.asyncio
async def test_set_value_success(mock_manager):
    wrapper = ConstanceConfigWrapper()
    wrapper.set_manager(mock_manager)

    await wrapper.set_value("TEST_KEY", 100)
    mock_manager.cache.set.assert_awaited_with("TEST_KEY", 100)


@pytest.mark.asyncio
async def test_set_value_without_manager():
    wrapper = ConstanceConfigWrapper()
    with pytest.raises(ImproperlyConfiguredError):
        await wrapper.set_value("TEST_KEY", 10)


@pytest.mark.asyncio
async def test_getattr_returns_config_value(mock_manager):
    wrapper = ConstanceConfigWrapper()
    wrapper.set_manager(mock_manager)

    value = await wrapper.TEST_KEY
    assert value == 42
