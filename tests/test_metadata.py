import iscc_sdk as idk


def test_extract_metadata(jpg_file):
    assert idk.extract_metadata(jpg_file).dict() == {
        "name": "Concentrated Cat",
        "creator": "Some Cat Lover",
        "height": 133,
        "width": 200,
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


def test_embed_metadata_unsupported(doc_file):
    meta = idk.IsccMeta(name="Some Title", description="Some Description")
    new_file = idk.embed_metadata(doc_file, meta)
    assert new_file is None
