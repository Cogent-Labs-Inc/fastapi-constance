from fastapi import status
from sqladmin import ModelView
from starlette.exceptions import HTTPException
from starlette.requests import Request

from fastapi_constance.models import ConstanceConfig


class ConstanceConfigAdmin(ModelView, model=ConstanceConfig):
    """
    SQLAdmin view for managing Constance configurations.

    This class validates admin edits against the runtime CONFIG passed during
    application startup. If a value doesn't match the declared type in CONFIG,
    an HTTP 400 error is raised immediately.

    - Prevents type mismatches (e.g., float entered where int is expected)
    - Disallows creation/deletion (only updates allowed)
    - Keeps default_value and description fields readonly
    """

    name = "Constance Config"
    name_plural = "Constance Configs"
    CONFIG = {}

    column_list = [
        ConstanceConfig.key,
        ConstanceConfig.default_value,
        ConstanceConfig.value,
        ConstanceConfig.description,
    ]

    column_labels = {
        "key": "Key",
        "default_value": "Default Value",
        "value": "Value",
        "description": "Description",
    }

    form_include_pk = True
    can_create = False
    can_delete = False

    form_excluded_columns = ["is_admin_modified"]

    form_widget_args = {
        "default_value": {
            "readonly": True,
            "style": "background-color: #f0f0f0; color: #555; cursor: not-allowed;",
        },
        "description": {
            "readonly": True,
            "style": "background-color: #f0f0f0; color: #555; cursor: not-allowed;",
        },
        "key": {
            "readonly": True,
            "style": "background-color: #f0f0f0; color: #555; cursor: not-allowed;",
        },
    }

    async def on_model_change(
        self,
        constance_config_data: dict,
        model: ConstanceConfig,
        is_created: bool,
        request: Request,
    ):
        """
        Called before saving a ConstanceConfig instance in SQLAdmin.
        Validates that the new value matches the expected type defined in CONFIG.
        """

        if not is_created and "value" in constance_config_data:
            key = constance_config_data.get("key") or model.key
            new_value = constance_config_data.get("value")

            config_type = self.CONFIG.get(key)
            if not config_type:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"'{key}' is not defined in CONFIG.",
                )

            expected_type = config_type.get("type", str)
            if expected_type is bool:
                if new_value not in ("True", "False"):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid value for '{key}'. Expected 'True' or 'False'.",
                    )
                casted_value = new_value == "True"
            else:
                try:
                    casted_value = expected_type(new_value)
                except (ValueError, TypeError):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid type for '{key}'. Expected {expected_type.__name__}.",
                    )

            constance_config_data["is_admin_modified"] = True
            from fastapi_constance.lifespan import constance_config

            constance_config.set_value(key, casted_value)

        await super().on_model_change(constance_config_data, model, is_created, request)
