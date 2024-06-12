"""*Metadata handling functions*"""

from typing import Optional

try:
    from pydantic.v1 import validator
except ImportError:  # pragma: no cover
    from pydantic import validator

import iscc_sdk as idk
import iscc_core as ic
import iscc_schema as iss

__all__ = [
    "extract_metadata",
    "embed_metadata",
    "IsccMeta",
]

EXTRACTORS = {
    "text": idk.text_meta_extract,
    "image": idk.image_meta_extract,
    "audio": idk.audio_meta_extract,
    "video": idk.video_meta_extract,
}

EMBEDDERS = {
    "text": idk.text_meta_embed,
    "image": idk.image_meta_embed,
    "audio": idk.audio_meta_embed,
    "video": idk.video_meta_embed,
}


def extract_metadata(fp):
    # type: (str) -> idk.IsccMeta
    """
    Extract metadata from file.

    :param str fp: Filepath to media file.
    :return: Metadata mapped to IsccMeta schema
    :rtype: IsccMeta
    """
    mime, mode = idk.mediatype_and_mode(fp)
    extractor = EXTRACTORS.get(mode)
    if extractor:
        metadata = extractor(fp)
        return idk.IsccMeta.construct(**metadata)


def embed_metadata(fp, meta):
    # type: (str, iss.IsccMeta) -> Optional[str]
    """
    Embed metadata into a copy of the media file and return path to updated file.

    :param str fp: Filepath to source media file
    :param IsccMeta meta: Metadata to embed into media file
    :return: Filepath to the new media file with embedded metadata (None if no embedding supported)
    :rtype: str|None
    """
    mime, mode = idk.mediatype_and_mode(fp)
    embedder = EMBEDDERS.get(mode)
    if embedder:
        new_file_path = embedder(fp, meta)
        return new_file_path


class IsccMeta(iss.IsccMeta):
    """Custom IsccMeta with text trimming support"""

    @validator("name", pre=True)
    def trim_name(cls, v):
        return ic.text_trim(v, idk.core_opts.meta_trim_name)

    @validator("description", pre=True)
    def trim_description(cls, v):
        return ic.text_trim(v, idk.core_opts.meta_trim_description)
