import pytest

import iscc_sdk as idk


def test_extract_metadata(jpg_file):
    assert idk.extract_metadata(jpg_file).dict() == {
        "name": "Concentrated Cat",
        "creator": "Some Cat Lover",
        "height": 133,
        "width": 200,
    }


def test_extract_metadata_unsupported(svg_file):
    with pytest.raises(idk.IsccUnsupportedMediatype):
        idk.extract_metadata(svg_file)


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


def test_embed_metadata_unsupported(doc_file):
    meta = idk.IsccMeta(name="Some Title", description="Some Description")
    new_file = idk.embed_metadata(doc_file, meta)
    assert new_file is None
