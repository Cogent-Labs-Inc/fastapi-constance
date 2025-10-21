from fastapi import status
from sqladmin import Admin, ModelView
from starlette.exceptions import HTTPException
from starlette.requests import Request

from fastapi_constance.config import CONFIG
from fastapi_constance.models import ConstanceConfig


class ConstanceConfigAdmin(ModelView, model=ConstanceConfig):
    name = "Constance Config"
    name_plural = "Constance Configs"

    column_list = [
        ConstanceConfig.key,
        ConstanceConfig.default_value,
        ConstanceConfig.value,
        ConstanceConfig.description,
    ]

    can_create = False
    can_delete = False

    form_excluded_columns = ["is_admin_modified"]

    form_widget_args = {
        "default_value": {"readonly": True},
        "description": {"readonly": True},
    }

    async def on_model_change(
        self,
        constance_config: dict,
        model: ConstanceConfig,
        is_created: bool,
        request: Request,
    ):
        """
        Called before saving a ConstanceConfig instance in the admin.
        Validates that the new value matches the expected type defined in CONFIG.
        For boolean keys, ensures the value is 'True' or 'False'.
        Marks the config as admin-modified if the value is updated.
        """

        if not is_created and "value" in constance_config:
            key = constance_config.get("key") or model.key
            new_value = constance_config.get("value")

            config_type = CONFIG.get(key)
            if config_type:
                expected_type = config_type.get("type", str)

                if expected_type is bool:
                    if new_value not in ("True", "False"):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=(
                                f"Invalid value for '{key}'. "
                                f"Expected 'True' or 'False', got '{new_value}'."
                            ),
                        )
                else:
                    try:
                        expected_type(new_value)
                    except (ValueError, TypeError):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=(
                                f"Invalid type for '{key}'. "
                                f"Expected {expected_type.__name__}, got value '{new_value}'."
                            ),
                        )

            constance_config["is_admin_modified"] = True

        await super().on_model_change(constance_config, model, is_created, request)


def setup_constance_admin(app, engine):
    if app is None or engine is None:
        raise RuntimeError(
            "FastAPI app and engine must be provided for SQLAdmin setup."
        )

    admin = Admin(app, engine)
    admin.add_view(ConstanceConfigAdmin)
    return admin
