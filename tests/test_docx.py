# -*- coding: utf-8 -*-
import iscc_sdk as idk


def test_extract_metadata_with_docx(docx_file):
    meta = idk.extract_metadata(docx_file)
    assert meta.dict() == {"creator": "titusz", "name": "title from metadata"}


def test_docx_meta_embed_name(docx_file):
    new_file = idk.docx_meta_embed(docx_file, idk.IsccMeta(name="New Title"))
    meta = idk.extract_metadata(new_file)
    assert meta.dict() == {"creator": "titusz", "name": "New Title"}


def test_docx_meta_embed_all(docx_file):
    meta = {
        "name": "The Title",
        "description": "The Description",
        "creator": "The Creator",
        "keywords": "The Keywords",
    }
    new_file = idk.docx_meta_embed(docx_file, idk.IsccMeta(**meta))
    new_meta = idk.extract_metadata(new_file)
    assert new_meta.dict() == meta


def test_embed_meta_with_docx(docx_file):
    new_file = idk.embed_metadata(docx_file, idk.IsccMeta(creator="Iñtërnâtiônàlizætiøn☃"))
    mime, mode = idk.mediatype_and_mode(new_file)
    assert mode == "text"
    assert mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    new_meta = idk.extract_metadata(new_file)
    assert new_meta.dict() == {"creator": "Iñtërnâtiônàlizætiøn☃", "name": "title from metadata"}


def test_embed_metadata_unsupported(doc_file):
    meta = idk.IsccMeta(name="Some Title", description="Some Description")
    new_file = idk.embed_metadata(doc_file, meta)
    assert new_file is None
