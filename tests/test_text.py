# -*- coding: utf-8 -*-
import iscc_sdk
import iscc_sdk as idk


def test_text_meta_extract_pdf(pdf_file):
    assert idk.text_meta_extract(pdf_file) == {"name": "title from metadata"}


def test_text_meta_extract_docx(docx_file):
    assert idk.text_meta_extract(docx_file) == {"creator": "titusz", "name": "title from metadata"}


def test_text_extract_pdf(pdf_file):
    text = iscc_sdk.text_extract(pdf_file)
    assert text.strip().startswith("Bitcoin: A Peer-to-Peer Electronic Cash System")


def test_text_extract_docx(docx_file):
    text = iscc_sdk.text_extract(docx_file)
    assert text.strip().startswith("ISCC Test Document")


def test_text_name_from_uri(jpg_file):
    assert idk.text_name_from_uri("http://example.com") == "example"
    assert idk.text_name_from_uri("http://example.com/some-file.txt") == "some file"
    assert idk.text_name_from_uri("http://example.com/some_file.txt?q=x") == "some file"
    assert idk.text_name_from_uri(jpg_file) == "img"
