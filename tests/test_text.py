# -*- coding: utf-8 -*-
from pathlib import Path

import pytest

import iscc_sdk as idk


def test_text_meta_extract_pdf(pdf_file):
    assert idk.text_meta_extract(pdf_file) == {"name": "title from metadata"}


def test_text_meta_extract_docx(docx_file):
    assert idk.text_meta_extract(docx_file) == {"creator": "titusz", "name": "title from metadata"}


def test_text_meta_extract_epub(epub_file):
    assert idk.text_meta_extract(epub_file) == {
        "name": "Children's Literature",
        "creator": "Charles Madison Curry, Erle Elsworth Clippinger",
        "rights": "Public domain in the USA.",
    }


def test_text_meta_embed_pdf(pdf_file):
    meta = {"name": "testname", "description": "testdescription"}
    new_file = idk.text_meta_embed(pdf_file, idk.IsccMeta(**meta))
    assert idk.text_meta_extract(new_file) == meta


def test_text_extract_pdf(pdf_file):
    text = idk.text_extract(pdf_file)
    assert text.strip().startswith("Bitcoin: A Peer-to-Peer Electronic Cash System")


def test_text_extract_empty(tmp_path):
    fp = tmp_path / "empty.txt"
    fp.write_text(" \n")
    with pytest.raises(idk.IsccExtractionError):
        idk.text_extract(fp)


def test_text_extract_docx(docx_file):
    text = idk.text_extract(docx_file)
    assert text.strip().startswith("ISCC Test Document")


def test_text_name_from_uri_str(jpg_file):
    assert idk.text_name_from_uri("http://example.com") == "example"
    assert idk.text_name_from_uri("http://example.com/some-file.txt") == "some file"
    assert idk.text_name_from_uri("http://example.com/some_file.txt?q=x") == "some file"
    assert idk.text_name_from_uri(jpg_file) == "img"


def test_text_name_from_uri_path(jpg_file):
    assert idk.text_name_from_uri(Path(jpg_file)) == "img"


def test_text_chunks(docx_file):
    txt = idk.text_extract(docx_file)
    chunks = list(idk.text_chunks(txt, avg_size=128))
    assert len(chunks) == 56
    assert "".join(chunks) == txt
    assert chunks[0] == (
        "ISCC Test Document\n"
        "\n"
        "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy "
        "eirmod tempor invid"
    )


def test_text_features(docx_file):
    txt = idk.text_extract(docx_file)
    features = idk.text_features(txt)
    assert features == {"kind": "text", "version": 0, "features": ["eGluK69boGk"], "sizes": [6069]}


def test_code_text_no_meta_extract(docx_file):
    idk.sdk_opts.extract_metadata = False
    meta = idk.code_text(docx_file)
    assert meta.dict() == {"characters": 4951, "iscc": "ISCC:EAAQMBEYQF6457DP"}
    idk.sdk_opts.extract_metadata = True
