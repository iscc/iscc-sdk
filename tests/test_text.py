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
    assert features == {
        "maintype": "content",
        "subtype": "text",
        "version": 0,
        "byte_offsets": False,
        "offsets": [0, 997, 1454, 2123, 4942, 5399, 6068],
        "simprints": [
            "k5TpwXVE3j9N5IBxm36c4hkXP6fHOv8bkY2f68_8XSg",
            "OERRAF2u5WWuLHZLZzgcCSoCoL9R0NYrBJD7s7A43t0",
            "AARYEMzu5WEOfTZq5ixNLcoThJ5AgJYNRICysqEs3v0",
            "lp6NgXnE_C1c6ij12-w04RwZN4XJyP0KgIrbKYX81yo",
            "OERRAF2u5WWuLHZLZzgcCSoCoL9R0NYrBJD7s7A43t0",
            "AARYEMzu5WEOfTZq5ixNLcoThJ5AgJYNRICysqEs3v0",
            "JfC6tnH1BuHFMviS2deReiUuelIIMvWWOozU6afjErU",
        ],
        "sizes": [997, 457, 669, 2819, 457, 669, 2],
    }


def test_text_features_stable(doc_file):
    expected = "j4Bo-QrY2phzOfDI2HMlm7t4kgipg5jRiSlIxBHD12I"

    # Robust changes: whitespace, case, control characters, marks (diacritics), and punctuation
    txt_a = "The ISCC is a similarity preserving fingerprint / identifier for digital media assets."
    txt_b = "The Iscc\n is a similärity preserving; fingerprint identifier for digital media assets"

    feat_a = idk.text_features(txt_a)["simprints"][0]
    feat_b = idk.text_features(txt_b)["simprints"][0]
    assert feat_a == expected
    assert feat_b == expected


def test_text_features_byte_offsets(docx_file):
    """Verify that char offsets/sizes map to byte offsets/sizes with UTF-32BE."""
    sample_text = idk.text_extract(docx_file)
    features = idk.text_features(sample_text)
    offsets = features["offsets"]
    sizes = features["sizes"]

    # Get the original chunks directly from text_chunks
    chunks = list(idk.text_chunks(sample_text, avg_size=idk.sdk_opts.text_avg_chunk_size))

    # Store the original text encoded as UTF-32BE (without BOM)
    utf32be_data = sample_text.encode("utf-32-be")

    assert len(offsets) == len(sizes) == len(chunks)

    for char_offset, char_size, original_chunk in zip(offsets, sizes, chunks):
        # Calculate expected byte offset and size
        byte_offset = char_offset * 4
        byte_size = char_size * 4

        # Read the byte slice from the UTF-32BE data
        retrieved_bytes = utf32be_data[byte_offset : byte_offset + byte_size]

        # Decode the bytes back to string
        decoded_chunk = retrieved_bytes.decode("utf-32-be")

        # Verify that the decoded chunk matches the original chunk content
        assert decoded_chunk == original_chunk


def test_code_text_no_meta_extract(docx_file, monkeypatch):
    monkeypatch.setattr(idk.sdk_opts, "extract_meta", False)
    meta = idk.code_text(docx_file)
    assert meta.dict() == {"characters": 4951, "iscc": "ISCC:EAAQMBEYQF6457DP"}


def test_text_sanitize():
    sample_html = """
        <div>This is a <b>book description</b> with some <script>alert('XSS');</script> and
        <style>.hidden{display:none;}</style> elements.
        <p>It has paragraphs &amp; special characters.</p>
        <p>And multiple paragraphs.</p></div>
        """
    assert idk.text_sanitize(sample_html) == (
        "This is a book description with some and elements. It has paragraphs & "
        "special characters. And multiple paragraphs."
    )


def test_text_sanitize_case_insensitive():
    sample_html = """
        <div>Test with <SCRIPT>alert('XSS');</SCRIPT> and
        <STYLE>.hidden{display:none;}</STYLE> elements.</div>
        """
    assert idk.text_sanitize(sample_html) == "Test with and elements."


def test_text_keep(epub_file, monkeypatch):
    monkeypatch.setattr(idk.sdk_opts, "text_keep", True)
    meta = idk.code_text(epub_file)
    assert meta.text.startswith("THE CONTENTS")


def test_text_sanitize_nested_script():
    malicious_html = (
        "Safe text <script>malicious <script>inner</script> content</script> remaining text."
    )
    expected = "Safe text content remaining text."
    assert idk.text_sanitize(malicious_html) == expected


def test_text_sanitize_large_input():
    # Construct a large input with a script block inserted in between.
    prefix = "A" * 1000
    suffix = "B" * 1000
    script_content = "X" * 5000
    malicious_html = f"{prefix}<script>{script_content}</script>{suffix}"
    # After removal, expect only the prefix and suffix concatenated (whitespace normalized).
    expected = f"{prefix}{suffix}"
    assert idk.text_sanitize(malicious_html) == expected


def test_text_sanitize_large_input_style():
    # Construct a large input with a style block inserted in between.
    prefix = "hello"
    suffix = "world"
    style_content = ("body { background: red; } " * 1000).strip()
    malicious_html = f"{prefix}<style>{style_content}</style>{suffix}"
    expected = f"{prefix}{suffix}"
    assert idk.text_sanitize(malicious_html) == expected


def test_text_features_utf8_byte_offsets():
    # Sample text with multi-byte characters
    sample_text = "Hello, 世界!"  # Chinese characters require 3 bytes each in UTF-8

    # First get features with character offsets (default)
    char_features = idk.text_features(sample_text)

    # Then get features with byte offsets
    byte_features = idk.text_features(sample_text, byte_offsets=True)

    # Verify the sizes are different - byte sizes should be larger due to multi-byte chars
    assert byte_features["sizes"][0] > char_features["sizes"][0]

    # Calculate expected byte size
    expected_byte_size = len(sample_text.encode("utf-8"))
    assert byte_features["sizes"][0] == expected_byte_size

    # Verify the chunks can be correctly reconstructed using byte offsets
    utf8_bytes = sample_text.encode("utf-8")
    for i, (offset, size) in enumerate(zip(byte_features["offsets"], byte_features["sizes"])):
        chunk_bytes = utf8_bytes[offset : offset + size]
        decoded = chunk_bytes.decode("utf-8")
        # With a single chunk, it should match the original text
        if i == 0:
            assert decoded == sample_text


def test_text_sanitize_img_event():
    # Verify that tags with dangerous attributes are completely removed.
    html = "<img src='nonexistent.jpg' onerror='alert(1)'> Some text"
    # The img tag should be stripped entirely.
    expected = "Some text"
    assert idk.text_sanitize(html) == expected
