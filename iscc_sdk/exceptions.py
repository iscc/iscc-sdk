# -*- coding: utf-8 -*-


class IsccError(Exception):
    pass


class IsccExtractionError(IsccError):
    pass


class IsccUnsupportedMediatype(IsccError):
    pass
