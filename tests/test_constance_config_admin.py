from unittest.mock import AsyncMock, patch

import pytest
from starlette.exceptions import HTTPException
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


@pytest.mark.asyncio
async def test_readonly_field_change(admin, model, mock_request):
    """
    Test that attempting to modify a readonly field ('default_value')
    raises an HTTPException with a 400 status code.
    """

    with pytest.raises(HTTPException) as exc_info:
        await admin.on_model_change(
            constance_config={"key": "MAX_USERS", "default_value": "999"},
            model=model,
            is_created=False,
            request=mock_request,
        )
    assert exc_info.value.status_code == 400
    assert "default_value is readonly" in exc_info.value.detail


@pytest.mark.asyncio
async def test_invalid_type(admin, model, mock_request):
    """
    Test that setting a value with an invalid type (e.g., non-integer for int field)
    raises an HTTPException with a 400 status code.
    """

    with pytest.raises(HTTPException) as exc_info:
        await admin.on_model_change(
            constance_config={"key": "MAX_USERS", "value": "invalid_int"},
            model=model,
            is_created=False,
            request=mock_request,
        )
    assert exc_info.value.status_code == 400
    assert "Invalid type for 'MAX_USERS'" in exc_info.value.detail


@pytest.mark.asyncio
async def test_valid_boolean_strings(admin, mock_request, mock_set_value):
    """
    Test that boolean fields correctly handle 'True'/'False' string inputs,
    convert them to bool types, and call set_value with correct parameters.
    """

    constance_config = {"key": "ENABLE_FEATURE", "value": "False"}
    model_bool = ConstanceConfig(key="ENABLE_FEATURE", value="True", default_value="True", description="Enable")

    await admin.on_model_change(
        constance_config=constance_config,
        model=model_bool,
        is_created=False,
        request=mock_request,
    )

    mock_set_value.assert_awaited_with("ENABLE_FEATURE", False)
    assert constance_config.get("is_admin_modified") is True


@pytest.mark.asyncio
async def test_invalid_config_key(admin, mock_request):
    """
    Test that attempting to modify a configuration key not defined in CONFIG
    raises an HTTPException with a 400 status code.
    """

    model_unknown = ConstanceConfig(key="UNKNOWN_KEY", value="123", default_value="123", description="Unknown")

    with pytest.raises(HTTPException) as exc_info:
        await admin.on_model_change(
            constance_config={"value": "456"},
            model=model_unknown,
            is_created=False,
            request=mock_request,
        )
    assert exc_info.value.status_code == 400
    assert "not defined in CONFIG" in exc_info.value.detail


@pytest.mark.asyncio
async def test_creation_skipped(admin, model, mock_request, mock_set_value):
    """
    Test that when a new configuration entry is created (is_created=True),
    the admin does not trigger the set_value call.
    """

    constance_config = {"key": "MAX_USERS", "value": "200"}

    await admin.on_model_change(
        constance_config=constance_config,
        model=model,
        is_created=True,
        request=mock_request,
    )

    mock_set_value.assert_not_awaited()
    assert model.key == "MAX_USERS"
