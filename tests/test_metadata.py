import shutil

import pytest

import iscc_sdk as idk


def test_extract_metadata(jpg_file):
    assert idk.extract_metadata(jpg_file).dict() == {
        "name": "Concentrated Cat",
        "creator": "Some Cat Lover",
        "height": 133,
        "width": 200,
    }


def test_extract_metadata_svg(svg_file):
    result = idk.extract_metadata(svg_file)
    assert result.dict() == {
        "name": "Red Circle",
        "description": "A simple red circle",
        "width": 100,
        "height": 100,
    }


def test_extract_metadata_unsupported(dat_file):
    with pytest.raises(idk.IsccUnsupportedMediatype):
        idk.extract_metadata(dat_file)


def test_extract_metadata_with_file_name(jpg_file, tmp_path):
    noext = tmp_path / "tempfile"
    shutil.copy(jpg_file, noext)
    result = idk.extract_metadata(noext, file_name="img.jpg")
    assert result.dict() == {
        "name": "Concentrated Cat",
        "creator": "Some Cat Lover",
        "height": 133,
        "width": 200,
    }


def test_extract_metadata_svg_with_file_name(svg_file, tmp_path):
    """SVG saved with .xml extension is correctly handled via file_name override."""
    xml_copy = tmp_path / "temp.xml"
    shutil.copy(svg_file, xml_copy)
    result = idk.extract_metadata(xml_copy, file_name="image.svg")
    assert result.dict() == {
        "name": "Red Circle",
        "description": "A simple red circle",
        "width": 100,
        "height": 100,
    }


def test_embed_metadata(jpg_file):
    meta = idk.IsccMeta(name="Some Title", description="Some Description")
    new_file = idk.embed_metadata(jpg_file, meta)
    assert idk.extract_metadata(new_file).dict() == {
        "name": "Some Title",
        "description": "Some Description",
        "creator": "Some Cat Lover",
        "height": 133,
        "width": 200,
    }


def test_metadata_identifier_field_image(jpg_file):
    meta = idk.IsccMeta(name="Some Title", description="Some Description", identifier="abcdefghijk")
    new_file = idk.embed_metadata(jpg_file, meta)
    assert idk.extract_metadata(new_file).dict() == {
        "name": "Some Title",
        "description": "Some Description",
        "creator": "Some Cat Lover",
        "height": 133,
        "width": 200,
        "identifier": "abcdefghijk",
    }


# def test_embed_metadata_image_acquire(jpg_file):
#     metadata = {
#         "name": "The Never Ending Story",
#         "description": "a 1984 fantasy film co-written and directed by *Wolfgang Petersen*",
#         "meta": "data:application/json;charset=utf-8;base64,eyJleHRlbmRlZCI6Im1ldGFkYXRhIn0=",
#         "creator": "Joanne K. Rowling",
#         "license": "https://example.com/license-terms-for-this-item",
#         "acquire": "https://example.com/buy-license-for-item-here",
#         "credit": "Frank Farian - Getty Images",
#         "rights": "Copyright 2022 ISCC Foundation - www.iscc.codes",
#     }
#     new_file = idk.embed_metadata(jpg_file, idk.IsccMeta.construct(**metadata))
#
#     assert idk.extract_metadata(new_file).dict() == {
#         "name": "The Never Ending Story",
#         "description": "a 1984 fantasy film co-written and directed by *Wolfgang Petersen*",
#         "meta": "data:application/json;charset=utf-8;base64,eyJleHRlbmRlZCI6Im1ldGFkYXRhIn0=",
#         "creator": "Joanne K. Rowling",
#         "license": "https://example.com/license-terms-for-this-item",
#         "acquire": "https://example.com/buy-license-for-item-here",
#         "credit": "Frank Farian - Getty Images",
#         "rights": "Copyright 2022 ISCC Foundation - www.iscc.codes",
#         "height": 133,
#         "width": 200,
#     }


def test_embed_metadata_with_outpath(jpg_file, tmp_path):
    meta = idk.IsccMeta(name="Some Title", description="Some Description")
    outpath = tmp_path / "subdir" / "output.jpg"
    new_file = idk.embed_metadata(jpg_file, meta, outpath=outpath)
    assert new_file == str(outpath)
    assert outpath.exists()
    assert idk.extract_metadata(new_file).dict() == {
        "name": "Some Title",
        "description": "Some Description",
        "creator": "Some Cat Lover",
        "height": 133,
        "width": 200,
    }


def test_embed_metadata_with_dict(jpg_file):
    meta = {"name": "Dict Title", "description": "Dict Description"}
    new_file = idk.embed_metadata(jpg_file, meta)
    assert idk.extract_metadata(new_file).dict() == {
        "name": "Dict Title",
        "description": "Dict Description",
        "creator": "Some Cat Lover",
        "height": 133,
        "width": 200,
    }


def test_embed_metadata_unsupported(doc_file):
    meta = idk.IsccMeta(name="Some Title", description="Some Description")
    new_file = idk.embed_metadata(doc_file, meta)
    assert new_file is None
