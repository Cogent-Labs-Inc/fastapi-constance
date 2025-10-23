from typing import Any, Dict

from fastapi_constance.exceptions import TypeMismatchError


class ConstanceConfigCacheManager:
    """
    Handles all cache-related responsibilities.
    """

    def __init__(self):
        self._cache: Dict[str, Any] = {}

    def get(self, key: str) -> Any:
        return self._cache.get(key)

    def set(self, key: str, value: Any):
        self._cache[key] = value

    def remove(self, key: str):
        self._cache.pop(key, None)

    def populate(self, config: Dict[str, dict]):
        """
        Initialize or refresh cache based on provided config structure.
        Ensures type safety for each cached value.
        """

        for key, data in config.items():
            value_type = data.get("type", str)
            cached_value = self.get(key)
            casted = self.type_cast_value(cached_value, value_type)
            self.set(key, casted)

    def type_cast_value(self, value: Any, value_type: type) -> Any:
        """
        Strictly handle type casting, especially for bools.
        """

        if value is None:
            return None

        if value_type is bool:
            if isinstance(value, str):
                if value == "True":
                    return True
                elif value == "False":
                    return False
                raise TypeMismatchError(
                    f"Cannot type cast '{value}' to bool. Must be 'True' or 'False'."
                )
            if isinstance(value, bool):
                return value
            raise TypeMismatchError(
                f"Cannot type cast '{value}' of type {type(value).__name__} to bool."
            )

        try:
            return value_type(value)
        except (ValueError, TypeError):
            raise TypeMismatchError(
                f"Cannot type cast value '{value}' to {value_type.__name__}"
            )
