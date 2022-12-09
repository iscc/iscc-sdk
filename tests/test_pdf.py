# -*- coding: utf-8 -*-
from PIL.Image import Image

import iscc_sdk as idk


meta = {
    "name": "Iñtërnâtiônàlizætiøn☃",
    "description": "Description CHANGED in PDF",
    "meta": "someuri",
    "creator": "Author CHANGED in PDF",
    "keywords": "Keywords CHANGED in PDF",
    "license": "http://example.com",
    "acquire": "http://example.com",
    "credit": "The Credit",
    "rights": "The Rights",
}


def test_extract_metadata(pdf_file):
    assert idk.extract_metadata(pdf_file).dict() == {"name": "title from metadata"}


def test_embed_metadata(pdf_file):
    new_file = idk.pdf_meta_embed(pdf_file, idk.IsccMeta(**meta))
    assert idk.extract_metadata(new_file) == meta


def test_embed_metadata_retains_existing(pdf_file):
    new_file = idk.pdf_meta_embed(pdf_file, idk.IsccMeta(description="via embedding"))
    assert idk.extract_metadata(new_file).dict() == {
        "name": "title from metadata",
        "description": "via embedding",
    }


def test_pdf_thumbnail(pdf_file):
    thumb = idk.pdf_thumbnail(pdf_file)
    assert isinstance(thumb, Image)


def test_text_thumbnail_with_pdf(pdf_file):
    thumb = idk.text_thumbnail(pdf_file)
    assert isinstance(thumb, Image)


def test_thumbnail_with_pdf(pdf_file):
    thumb = idk.thumbnail(pdf_file)
    assert isinstance(thumb, Image)
