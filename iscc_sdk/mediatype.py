"""*Detect and map RFC6838 mediatypes to ISCC processing modes*."""
from os.path import basename

from loguru import logger as log
from typing import List, Optional, Union
import mimetypes
import magic


__all__ = [
    "mediatype_and_mode",
    "mediatype_guess",
    "mediatype_normalize",
    "mediatype_supported",
    "mediatype_clean",
    "mediatype_to_mode",
    "mediatype_from_name",
    "mediatype_from_data",
    "SUPPORTED_MEDIATYPES",
    "SUPPORTED_EXTENSIONS",
]


def mediatype_and_mode(fp):
    # type: (str) -> tuple
    """
    Detect mediatype and processing mode for a file.

    !!! example
        ```
        >>> import iscc_sdk
        >>> iscc_sdk.mediatype_and_mode('some.pdf')
        ('application/pdf', 'text')

        ```

    :param str fp: Filepath
    :return: A tuple of `mediatype` and `mode`
    :rtype: tuple[str, str]
    """
    with open(fp, "rb") as infile:
        data = infile.read(4096)

    mediatype = mediatype_guess(data, file_name=basename(fp))
    mode = mediatype_to_mode(mediatype)
    return mediatype, mode


def mediatype_guess(data, file_name=None):
    # type: (bytes, Optional[str]) -> str
    """
    Guess mediatype from raw data or filename.

    First try to guess by file extension. If that fails we match by content sniffing.

    !!! example
        ```
        >>> import iscc_sdk
        >>> iscc_sdk.mediatype_guess(b'GIF89a')
        'image/gif'

        ```

    :param bytes data: Raw file data (first 4096 bytes recommended)
    :param Optional[str] file_name: Filename for guessing based on file extension
    :return: Media type sting
    :rtype: str
    """
    guess_name, guess_data = None, None

    if file_name:
        guess_name = mediatype_from_name(file_name)

    guess_data = mediatype_from_data(data)

    # Normalize
    guess_data = mediatype_normalize(guess_data)
    guess_name = mediatype_normalize(guess_name)
    media_type = guess_name or guess_data

    # Special cases of missdetection
    if guess_data and "ogg" in guess_data:
        media_type = guess_data

    log.debug(f"{media_type} mediatype detected")

    return media_type


def mediatype_normalize(mime):
    # type: (str) -> str
    """
    Normalize mediatype string.

    !!! example
        ```
        >>> import iscc_sdk
        >>> iscc_sdk.mediatype_normalize("audio/x-aiff")
        '"audio/aiff"'

        ```

    :param str mime: Mediatype sting
    :return: Normalized mediatype string
    :rtype: str
    """
    return MEDIATYPE_NORM.get(mime, mime)


def mediatype_supported(mime):
    # type: (str) -> bool
    """
    Check if mediatype is supported.

    :param str mime: Mediatype sting
    :return: True if mediatype is supported
    :rtype: bool
    """
    return mediatype_normalize(mime) in SUPPORTED_MEDIATYPES


def mediatype_from_name(name):
    # type: (str) -> Optional[str]
    """
    Guess mediatype from filename or URL.

    :param str name: Filename or URL
    :return: Mediatype string
    :rtype: str
    """
    return mimetypes.guess_type(name)[0]


def mediatype_from_data(data):
    # type: (bytes) -> Optional[str]
    """
    Guess mediatype by sniffing raw header data.

    :param bytes data: Raw fileheader data (first 4096 bytes recommended)
    :return: Mediatype string
    :rtype: str
    """
    return magic.from_buffer(data, mime=True)


def mediatype_clean(mime):
    # type: (Union[str, List]) -> str
    """
    Clean mediatype/content-type string or first entry of a list of mimetype strings.

    Also removes semicolon separated encoding information.

    :param Union[str, List] mime: Mediatype or list of mediatypes
    :return: Mediatype string
    :rtype: str
    """
    if mime and isinstance(mime, List):
        mime = mime[0]
    if mime:
        mime = mime.split(";")[0]
    return mime.strip()


def mediatype_to_mode(mime_type):
    # type: (str) -> str
    """Get perceptual processing mode from mimetype.

    :param str mime_type: RFC-6838 mediatype string
    :return str: Processing mode ("text", "image", "audio", "video")
    :raise ValueError: if no matching processing mode was found.
    """

    mime_type = mediatype_clean(mime_type)
    entry = SUPPORTED_MEDIATYPES.get(mime_type)
    if entry:
        return entry["mode"]

    # Fallback to guess mode by top-level type
    mode = mime_type.split("/")[0]
    if mode in ["text", "image", "audio", "video"]:
        log.warning(f"Guessing perceptual mode from {mime_type}")
        return mode

    raise ValueError(f"No known processing mode for {mime_type}")


mimetypes.add_type("text/markdown", ".md")
mimetypes.add_type("text/markdown", ".markdown")
mimetypes.add_type("application/x-mobipocket-ebook", ".mobi")
mimetypes.add_type("application/x-sqlite3", ".sqlite")
mimetypes.add_type("video/mp4", ".f4v")
mimetypes.add_type("video/h264", ".h264")


SUPPORTED_MEDIATYPES = {
    # Text Formats
    "application/rtf": {"mode": "text", "ext": "rtf"},
    "application/msword": {"mode": "text", "ext": "doc"},
    "application/pdf": {"mode": "text", "ext": "pdf"},
    "application/epub+zip": {"mode": "text", "ext": "epub"},
    "text/xml": {"mode": "text", "ext": "xml"},
    "application/json": {"mode": "text", "ext": "json"},
    "application/xhtml+xml": {"mode": "text", "ext": "xhtml"},
    "application/vnd.oasis.opendocument.text": {"mode": "text", "ext": "odt"},
    "text/html": {"mode": "text", "ext": "html"},
    "text/plain": {"mode": "text", "ext": "txt"},
    "application/x-ibooks+zip": {"mode": "text", "ext": "ibooks"},
    "text/markdown": {"mode": "text", "ext": ["md", "markdown"]},
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": {
        "mode": "text",
        "ext": "docx",
    },
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {
        "mode": "text",
        "ext": "xlsx",
    },
    # Note: pptx only detected by file extension. Sniffing gives 'application/zip'
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": {
        "mode": "text",
        "ext": "pptx",
    },
    "application/vnd.ms-excel": {"mode": "text", "ext": "xls"},
    "application/x-mobipocket-ebook": {
        "mode": "text",
        "ext": ["mobi", "prc", "azw", "azw3", "azw4"],
    },
    # Image Formats
    "image/bmp": {"mode": "image", "ext": "bmp"},
    "image/gif": {"mode": "image", "ext": "gif"},
    "image/jpeg": {"mode": "image", "ext": ["jpg", "jpeg"]},
    "image/png": {"mode": "image", "ext": "png"},
    "image/tiff": {"mode": "image", "ext": "tif"},
    "image/vnd.adobe.photoshop": {"mode": "image", "ext": "psd"},
    "application/postscript": {"mode": "image", "ext": "eps"},
    # Audio Formats
    "audio/mpeg": {"mode": "audio", "ext": "mp3"},
    "audio/wav": {"mode": "audio", "ext": "wav"},
    "audio/x-wav": {"mode": "audio", "ext": "wav"},
    "audio/ogg": {"mode": "audio", "ext": "ogg"},
    "audio/aiff": {"mode": "audio", "ext": "aif"},
    "audio/x-aiff": {"mode": "audio", "ext": "aif"},
    "audio/x-flac": {"mode": "audio", "ext": "flac"},
    "audio/opus": {"mode": "audio", "ext": "opus"},
    # Video Formats
    "application/vnd.rn-realmedia": {"mode": "video", "ext": "rm"},
    "video/x-dirac": {"mode": "video", "ext": "drc"},
    "video/3gpp": {"mode": "video", "ext": "3gp"},
    "video/3gpp2": {"mode": "video", "ext": "3g2"},
    "video/x-ms-asf": {"mode": "video", "ext": "asf"},
    "video/avi": {"mode": "video", "ext": "avi"},
    "video/webm": {"mode": "video", "ext": "webm"},
    "video/mpeg": {"mode": "video", "ext": ["mpeg", "mpg", "m1v", "vob"]},
    "video/mp4": {"mode": "video", "ext": "mp4"},
    "video/x-m4v": {"mode": "video", "ext": "m4v"},
    "video/x-matroska": {"mode": "video", "ext": "mkv"},
    "video/ogg": {"mode": "video", "ext": ["ogg", "ogv"]},
    "video/quicktime": {"mode": "video", "ext": ["mov", "f4v"]},
    "video/x-flv": {"mode": "video", "ext": "flv"},
    "application/x-shockwave-flash": {"mode": "video", "ext": "swf"},
    "video/h264": {"mode": "video", "ext": "h264"},
    "video/x-ms-wmv": {"mode": "video", "ext": "wmv"},
}

MEDIATYPE_NORM = {
    "audio/x-aiff": "audio/aiff",
    "audio/x-wav": "audio/wav",
    "image/x-ms-bmp": "image/bmp",
    "video/x-msvideo": "video/avi",
}

SUPPORTED_EXTENSIONS = []
for v in SUPPORTED_MEDIATYPES.values():
    ext = v["ext"]
    if isinstance(ext, str):
        SUPPORTED_EXTENSIONS.append(ext)
    else:
        for e in ext:
            SUPPORTED_EXTENSIONS.append(e)
