from unittest.mock import AsyncMock, patch

import pytest
from starlette.requests import Request

from fastapi_constance.admin import ConstanceConfigAdmin
from fastapi_constance.lifespan import constance_config as lifespan_constance_config
from fastapi_constance.models import ConstanceConfig

CONFIG = {
    "MAX_USERS": {"type": int, "value": 100},
    "ENABLE_FEATURE": {"type": bool, "value": True},
    "APP_NAME": {"type": str, "value": "TestApp"},
}


@pytest.fixture
def admin():
    """
    Fixture that returns a configured instance of ConstanceConfigAdmin
    with a predefined CONFIG for testing.
    """
    admin_instance = ConstanceConfigAdmin()
    admin_instance.CONFIG = CONFIG
    return admin_instance


@pytest.fixture
def model():
    """
    Fixture that creates a mock ConstanceConfig model instance representing
    a configuration entry in the database.
    """
    return ConstanceConfig(key="MAX_USERS", value="100", default_value="100", description="Maximum users")


@pytest.fixture
def mock_request():
    """
    Fixture that returns a mock Starlette Request object for simulating
    incoming HTTP requests to the admin view.
    """
    return Request({"type": "http", "method": "POST", "headers": {}})


@pytest.fixture
def mock_set_value():
    """
    Fixture that patches the lifespan constance_config.set_value method
    with an AsyncMock to prevent actual configuration updates.
    """
    with patch.object(lifespan_constance_config, "set_value", new_callable=AsyncMock) as mock_method:
        yield mock_method
