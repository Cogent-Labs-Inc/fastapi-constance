class NotSupportedTypeError(Exception):
    """Raised when a type other than int, float, str, or bool is used."""

    pass


class TypeMismatchError(Exception):
    """Raised when a stored or default value does not match the defined type."""

    pass


class ImproperlyConfiguredError(Exception):
    """Raised when the application is not properly configured."""

    pass
