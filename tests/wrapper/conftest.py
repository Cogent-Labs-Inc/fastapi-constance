from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def mock_manager():
    """Fixture that provides a mock manager with async cache behavior."""

    manager = MagicMock()
    manager.config = {"TEST_KEY": {"type": int, "value": 10}}
    manager.cache = MagicMock()
    manager.cache.get = AsyncMock(return_value="42")
    manager.cache.type_cast_value = MagicMock(return_value=42)
    manager.cache.set = AsyncMock()
    return manager
