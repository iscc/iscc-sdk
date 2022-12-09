from PIL.Image import Image

import iscc_sdk as idk


def test_epub_thumbnail(epub_file):
    thumb = idk.epub_thumbnail(epub_file)
    assert isinstance(thumb, Image)


def test_text_thumbnail_with_epub(epub_file):
    thumb = idk.text_thumbnail(epub_file)
    assert isinstance(thumb, Image)


def test_thumbnail_with_epub(epub_file):
    thumb = idk.thumbnail(epub_file)
    assert isinstance(thumb, Image)


def test_epub_extract_metadata(epub_file):
    meta = idk.extract_metadata(epub_file)
    assert meta.dict() == {
        "name": "Children's Literature",
        "creator": "Charles Madison Curry, Erle Elsworth Clippinger",
        "rights": "Public domain in the USA.",
    }


def test_epub_meta_embed(epub_file):
    meta = idk.IsccMeta(
        name="Name", description="Description", creator="Creator", keywords="some, keywords"
    )
    new_file = idk.epub_meta_embed(epub_file, meta)
    meta = idk.extract_metadata(new_file)
    assert meta.dict() == {
        "description": "Description",
        "name": "Children's Literature",
        "creator": "Creator",
        "rights": "Public domain in the USA.",
    }
