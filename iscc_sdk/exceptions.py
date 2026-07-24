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
