"""*Text handling functions*."""
import json
import subprocess
import sys
from os.path import basename, splitext
from pathlib import Path
from urllib.parse import urlparse
from loguru import logger as log
import iscc_sdk as idk


__all__ = [
    "text_meta_extract",
    "text_extract",
    "text_name_from_uri",
]


TEXT_META_MAP = {
    "custom:iscc_name": "name",
    "custom:iscc_description": "description",
    "custom:iscc_meta": "meta",
    "dc:title": "name",
    "dc:description": "description",
    "dc:creator": "creator",
    "dc:rights": "rights",
}


def text_meta_extract(fp):
    # type: (str) -> dict
    """
    Extract metadata from text document file.

    :param str fp: Filepath to text document file.
    :return: Metadata mapped to IsccMeta schema
    :rtype: dict
    """
    args = ["--metadata", "-j", "--encoding=UTF-8", fp]

    result = idk.run_tika(args)
    meta = json.loads(result.stdout.decode(sys.stdout.encoding, errors="ignore"))
    mapped = dict()
    done = set()
    for tag, mapped_field in TEXT_META_MAP.items():
        if mapped_field in done:  # pragma nocover
            continue
        value = meta.get(tag)
        if value:
            if isinstance(value, list):
                value = ", ".join(value)
            log.debug(f"Mapping text metadata: {tag} -> {mapped_field} -> {value}")
            mapped[mapped_field] = value
            done.add(mapped_field)
    return mapped


def text_extract(fp):
    # type: (str) -> str
    """
    Extract plaintext from a text document.

    :param st fp: Filepath to text document file.
    :return: Extracted plaintext
    :rtype: str
    """

    args = ["--text", "--encoding=UTF-8", fp]
    result = idk.run_tika(args)
    text = result.stdout.decode(encoding="UTF-8").strip()
    if not text:
        raise idk.IsccExtractionError(f"No text extracted from {basename(fp)}")
    return result.stdout.decode(encoding="UTF-8")


def text_name_from_uri(uri):
    # type: (str, Path) -> str
    """
    Extract "filename" part of an uri without file extension to be used as fallback title for an
    asset if no title information can be acquired.

    :param str uri: Url or file path
    :return: derived name (might be an empty string)
    :rtype: str
    """
    if isinstance(uri, Path):
        result = urlparse(uri.as_uri())
    else:
        result = urlparse(uri)

    base = basename(result.path) if result.path else basename(result.netloc)
    name = splitext(base)[0]
    name = name.replace("-", " ")
    name = name.replace("_", " ")
    return name
