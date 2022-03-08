# -*- coding: utf-8 -*-
import iscc_sdk as idk


def test_text_name_from_uri(jpg_file):
    assert idk.text_name_from_uri("http://example.com") == "example"
    assert idk.text_name_from_uri("http://example.com/some-file.txt") == "some file"
    assert idk.text_name_from_uri("http://example.com/some_file.txt?q=x") == "some file"
    assert idk.text_name_from_uri(jpg_file) == "img"
