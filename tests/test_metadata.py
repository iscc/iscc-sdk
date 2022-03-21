import iscc_sdk as idk
import iscc_schema as iss


def test_extract_metadata(jpg_file):
    assert idk.extract_metadata(jpg_file).dict() == {
        "name": "Concentrated Cat",
        "creator": "Some Cat Lover",
        "height": 133,
        "width": 200,
    }


def test_embed_metadata(jpg_file):
    meta = iss.IsccMeta(name="Some Title", description="Some Description")
    new_file = idk.embed_metadata(jpg_file, meta)
    assert idk.extract_metadata(new_file).dict() == {
        "name": "Some Title",
        "description": "Some Description",
        "creator": "Some Cat Lover",
        "height": 133,
        "width": 200,
    }


def test_embed_metadata_unsupported(docx_file):
    meta = iss.IsccMeta(name="Some Title", description="Some Description")
    new_file = idk.embed_metadata(docx_file, meta)
    assert new_file is None
