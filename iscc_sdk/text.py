"""*Text handling functions*."""
import json
import sys
from os.path import basename, splitext
from pathlib import Path
from typing import Generator
from urllib.parse import urlparse

import xxhash
from loguru import logger as log
import iscc_sdk as idk
import iscc_core as ic

__all__ = [
    "text_meta_extract",
    "text_extract",
    "text_features",
    "text_chunks",
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


def text_features(text):
    # type: (str) -> dict
    """
    Create granular fingerprint for text (minhashes over ngrams from cdc-chunks).
    Text should be normalized before extracting text features.

    :param str text: Normalized plaintext.
    :returns dict: Dictionary with 'sizes' and 'features'.
    """
    clean_text = ic.text_clean(text)
    chunks = text_chunks(clean_text, avg_size=idk.sdk_opts.text_avg_chunk_size)
    sizes = []
    feats = []
    for chunk in chunks:
        ngrams = (
            "".join(chars) for chars in ic.sliding_window(chunk, idk.sdk_opts.text_ngram_size)
        )
        features = [xxhash.xxh32_intdigest(s.encode("utf-8")) for s in ngrams]
        minimum_hash_digest = ic.alg_minhash_64(features)
        sizes.append(len(chunk))
        feats.append(ic.encode_base64(minimum_hash_digest))
    return dict(kind="text", version=0, features=feats, sizes=sizes)


def text_chunks(text, avg_size=idk.sdk_opts.text_avg_chunk_size):
    # type: (str, int) -> Generator[str]
    """
    Generates variable sized text chunks (without leading BOM)
    :param text: normalized plaintext
    :parm: avg_size: Targeted average size of text chunks in bytes.
    """
    data = text.encode("utf-32-be")
    avg_size *= 4  # 4 bytes per character
    for chunk in ic.alg_cdc_chunks(data, utf32=True, avg_chunk_size=avg_size):
        yield chunk.decode("utf-32-be")


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
