"""*Metadata handling functions*"""

import shutil

from loguru import logger as log
from pathlib import Path
from typing import Optional, List, Dict, Any


from pydantic import field_validator

import iscc_sdk as idk
import iscc_lib as il
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
    # type: (str|Path) -> idk.IsccMeta
    """
    Extract metadata from file.

    :param fp: Filepath to media file.
    :return: Metadata mapped to IsccMeta schema
    """
    fp = Path(fp)
    mime, mode = idk.mediatype_and_mode(fp)
    extractor = EXTRACTORS.get(mode)
    if extractor:
        metadata = extractor(fp)
        return idk.IsccMeta.model_construct(**metadata)


def embed_metadata(fp, meta, outpath=None):
    # type: (str, iss.IsccMeta|dict, Optional[str|Path]) -> Optional[str]
    """
    Embed metadata into a copy of the media file and return path to updated file.

    :param str fp: Filepath to source media file
    :param meta: Metadata to embed (IsccMeta or dict)
    :param outpath: Optional output filepath. If None, creates a temp file.
    :return: Filepath to the new media file with embedded metadata (None if no embedding supported)
    :rtype: str|None
    """
    if isinstance(meta, dict):
        meta = idk.IsccMeta.model_construct(**meta)
    mime, mode = idk.mediatype_and_mode(fp)
    embedder = EMBEDDERS.get(mode)
    if embedder:
        new_file_path = embedder(fp, meta)
        if new_file_path and outpath:
            outpath = Path(outpath)
            outpath.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(new_file_path), str(outpath))
            return str(outpath)
        return new_file_path


class IsccMeta(iss.IsccMeta):
    """Custom IsccMeta with text trimming and recursive `parts` support"""

    parts: Optional[List[Dict[str, Any]]] = None

    @field_validator("name", mode="before")
    @classmethod
    def trim_name(cls, v):
        return il.text_trim(v, idk.core_opts.meta_trim_name)

    @field_validator("description", mode="before")
    @classmethod
    def trim_description(cls, v):
        return il.text_trim(v, idk.core_opts.meta_trim_description)
