import tempfile
from pathlib import Path

from docx import Document
import iscc_sdk as idk
import shutil

__all__ = [
    "docx_meta_embed",
]


META_DOCX_MAP = {
    "name": "title",
    "description": "comments",
    "creator": "author",
    "keywords": "keywords",
}


def docx_meta_embed(fp, meta):
    # type: (str|Path, idk.IsccMeta) -> str
    """
    Embed metadata into a copy of the DOCX file.

    :param fp: Filepath to source DOCX file
    :param meta: Metadata to embed into DOCX
    :return: Filepath to the new DOCX file with updated metadata
    """
    fp = Path(fp)
    tempdir = tempfile.mkdtemp()
    tempdoc = shutil.copy(fp, tempdir)
    doc = Document(fp.as_posix())
    new_meta = doc.core_properties
    for iscc_field, docx_field in META_DOCX_MAP.items():
        value = getattr(meta, iscc_field)
        if value:
            setattr(new_meta, docx_field, value)
    doc.save(tempdoc)
    return tempdoc
