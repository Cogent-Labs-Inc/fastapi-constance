from fastapi_constance.exceptions import (NotSupportedTypeError,
                                          TypeMismatchError)


class ConstanceConfigValidator:
    SUPPORTED_TYPES = (int, float, str, bool)

    def validate_all(self, config: dict):
        """Validate all config entries for required keys and types."""

        self._validate_required_keys(config)
        self._validate_types(config)

    def _validate_required_keys(self, config: dict):
        required_keys = ["value", "description", "type"]
        for key, data in config.items():
            for required_key in required_keys:
                if required_key not in data:
                    raise KeyError(
                        f"Missing '{required_key}' for key '{key}' in config"
                    )

    def _validate_types(self, config: dict):
        for key, data in config.items():
            value, value_type = data["value"], data.get("type")
            if value_type not in self.SUPPORTED_TYPES:
                raise NotSupportedTypeError(
                    f"Type {value_type.__name__} not supported for key '{key}'"
                )
            if not isinstance(value, value_type):
                raise TypeMismatchError(
                    f"Default value for '{key}' must be of type {value_type.__name__}, "
                    f"got {type(value).__name__}"
                )
