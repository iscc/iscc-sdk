"""*PDF handling module*."""

import shutil
import tempfile
from PIL import Image, ImageEnhance
import fitz
import iscc_sdk as idk

__all__ = [
    "pdf_thumbnail",
    "pdf_meta_embed",
]


def pdf_thumbnail(fp):
    # type: (str) -> Image.Image
    """
    Create a thumbnail from PDF document.

    :param str fp: Filepath to PDF document.
    :return: Thumbnail image as PIL Image object
    :rtype: Image.Image
    """
    with fitz.Document(fp) as doc:
        page = doc.load_page(0)
        pix = page.get_pixmap()
        mode = "RGBA" if pix.alpha else "RGB"
        img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
        size = idk.sdk_opts.image_thumbnail_size
        img.thumbnail((size, size), resample=idk.LANCZOS)
        return ImageEnhance.Sharpness(img.convert("RGB")).enhance(1.4)


def pdf_meta_embed(fp, meta):
    # type: (str, idk.IsccMeta) -> str
    """
    Embed metadata into a copy of the PDF file.

    :param str fp: Filepath to source PDF file
    :param IsccMeta meta: Metadata to embed into PDF
    :return: Filepath to the new PDF file with updated metadata
    :rtype: str
    """
    tempdir = tempfile.mkdtemp()
    temppdf = shutil.copy(fp, tempdir)
    with fitz.Document(temppdf) as doc:
        doc.del_xml_metadata()
        new_meta = doc.metadata or {}
        what, value = doc.xref_get_key(-1, "Info")  # /Info key in the trailer
        xref = int(value.replace("0 R", ""))

        if meta.name:
            new_meta["title"] = meta.name
            doc.xref_set_key(xref, "iscc_name", fitz.get_pdf_str(meta.name))
        if meta.description:
            new_meta["subject"] = meta.description
            doc.xref_set_key(xref, "iscc_description", fitz.get_pdf_str(meta.description))
        if meta.creator:
            new_meta["author"] = meta.creator
        if meta.keywords:
            new_meta["keywords"] = meta.keywords
        if meta.meta:
            doc.xref_set_key(xref, "iscc_meta", fitz.get_pdf_str(meta.meta))
        if meta.license:
            doc.xref_set_key(xref, "iscc_license", fitz.get_pdf_str(meta.license))
        if meta.acquire:
            doc.xref_set_key(xref, "iscc_acquire", fitz.get_pdf_str(meta.acquire))
        if meta.credit:
            doc.xref_set_key(xref, "iscc_credit", fitz.get_pdf_str(meta.credit))
        if meta.rights:
            doc.xref_set_key(xref, "iscc_rights", fitz.get_pdf_str(meta.rights))
        doc.set_metadata(new_meta)
        doc.saveIncr()
    return temppdf
