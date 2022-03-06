import iscc_sdk as idk


def test_code_image(jpg_file):
    assert idk.code_image(jpg_file).dict(exclude_unset=True) == {
        "creator": "Some Cat Lover",
        "height": 133,
        "iscc": "ISCC:EEA4GQZQTY6J5DTH",
        "name": "Concentrated Cat",
        "thumbnail": "data:image/webp;base64,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",
        "width": 200,
    }
