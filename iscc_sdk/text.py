"""*Text handling functions*."""
from os.path import basename, splitext
from urllib.parse import urlparse


__all__ = ["text_name_from_uri"]


def text_name_from_uri(uri):
    # type: (str) -> str
    """
    Extract "filename" part of an uri without file extension to be uses as fallback title for an
    asset if no title information can be aquired.

    :param str uri: Url or file path
    :return: derived name (might be an empty string)
    :rtype: str
    """
    result = urlparse(uri)

    base = basename(result.path) if result.path else basename(result.netloc)
    name = splitext(base)[0]
    name = name.replace("-", " ")
    name = name.replace("_", " ")
    return name
