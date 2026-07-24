"""*PDF handling module*."""

import shutil
import tempfile
from pathlib import Path

import pypdfium2 as pdfium
from PIL import ImageEnhance
from pypdf import PdfReader, PdfWriter

import iscc_sdk as idk

__all__ = [
    "pdf_meta_embed",
    "pdf_text_extract",
    "pdf_thumbnail",
]


_ISCC_META_KEYS = (
    ("name", "/iscc_name"),
    ("description", "/iscc_description"),
    ("meta", "/iscc_meta"),
    ("license", "/iscc_license"),
    ("acquire", "/iscc_acquire"),
    ("credit", "/iscc_credit"),
    ("rights", "/iscc_rights"),
)


def pdf_text_extract(fp):
    # type: (str|Path) -> str
    """Extract PDF text using pypdfium2's bounded text page API."""
    fp = Path(fp)
    doc = pdfium.PdfDocument(str(fp))
    try:
        return "\n".join(page.get_textpage().get_text_bounded() for page in doc)
    finally:
        doc.close()


def pdf_thumbnail(fp):
    # type: (str|Path) -> Image.Image
    """
    Create a thumbnail from PDF document.

    :param fp: Filepath to PDF document.
    :return: Thumbnail image as PIL Image object
    """
    fp = Path(fp)
    doc = pdfium.PdfDocument(str(fp))
    try:
        img = doc[0].render().to_pil()
    finally:
        doc.close()
    size = idk.sdk_opts.image_thumbnail_size
    img.thumbnail((size, size), resample=idk.LANCZOS)
    return ImageEnhance.Sharpness(img.convert("RGB")).enhance(1.4)


def pdf_meta_embed(fp, meta):
    # type: (str|Path, idk.IsccMeta) -> Path
    """
    Embed metadata into a copy of the PDF file.

    :param fp: Filepath to source PDF file
    :param meta: Metadata to embed into PDF
    :return: Filepath to the new PDF file with updated metadata
    """
    fp = Path(fp)
    tempdir = tempfile.mkdtemp()
    temppdf = Path(shutil.copy(fp, tempdir))

    reader = PdfReader(str(temppdf))
    writer = PdfWriter(clone_from=reader)

    updates = {}
    if meta.name:
        updates["/Title"] = meta.name
    if meta.description:
        updates["/Subject"] = meta.description
    if meta.creator:
        updates["/Author"] = meta.creator
    if meta.keywords:
        updates["/Keywords"] = meta.keywords
    for attr, key in _ISCC_META_KEYS:
        value = getattr(meta, attr, None)
        if value:
            updates[key] = value

    if updates:
        writer.add_metadata(updates)

    with open(temppdf, "wb") as f:
        writer.write(f)

    return temppdf
