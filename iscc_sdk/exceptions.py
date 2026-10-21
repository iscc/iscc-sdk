"""*Exceptions raised by iscc-sdk*"""

__all__ = [
    "EnvironmentError",
    "IsccError",
    "IsccExtractionError",
    "IsccThumbExtractionError",
    "IsccUnsupportedMediatype",
]


class IsccError(Exception):
    pass


class IsccExtractionError(IsccError):
    pass


class IsccThumbExtractionError(IsccExtractionError):
    pass


class IsccUnsupportedMediatype(IsccError):
    pass


class EnvironmentError(IsccError):
    pass
