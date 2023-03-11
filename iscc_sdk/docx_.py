import tempfile
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
    # type: (str, idk.IsccMeta) -> str
    """
    Embed metadata into a copy of the PDF file.
    :param str fp: Filepath to source PDF file
    :param IsccMeta meta: Metadata to embed into PDF
    :return: Filepath to the new PDF file with updated metadata
    :rtype: str
    """
    tempdir = tempfile.mkdtemp()
    tempdoc = shutil.copy(fp, tempdir)
    doc = Document(fp)
    new_meta = doc.core_properties
    for iscc_field, docx_field in META_DOCX_MAP.items():
        value = getattr(meta, iscc_field)
        if value:
            setattr(new_meta, docx_field, value)
    doc.save(tempdoc)
    return tempdoc
