import pytest
from starlette.exceptions import HTTPException

from fastapi_constance.models import ConstanceConfig


@pytest.mark.asyncio
class TestConstanceConfigAdmin:
    """
    Test suite for the ConstanceConfigAdmin class, covering all major
    configuration update and validation scenarios.
    """

    async def test_readonly_field_change(self, admin, model, mock_request):
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

    async def test_invalid_type(self, admin, model, mock_request):
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

    async def test_valid_boolean_strings(self, admin, mock_request, mock_set_value):
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

    async def test_invalid_config_key(self, admin, mock_request):
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

    async def test_creation_skipped(self, admin, model, mock_request, mock_set_value):
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
