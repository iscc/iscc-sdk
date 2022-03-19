import pytest

import iscc_sdk as idk
from iscc_samples import texts


def test_code_iscc_image(jpg_file):
    assert idk.code_iscc(jpg_file).dict() == {
        "creator": "Some Cat Lover",
        "datahash": "1e2055529bfae5bdb3d530c52f44d13ccd6a7c710f63620dc2db1c43c5592ae2dc97",
        "filesize": 35393,
        "height": 133,
        "iscc": "ISCC:KECWRY3VY6R5SNV4YNBTBHR4T2HGP3HKVFO7TYUP2BKVFG724W63HVI",
        "mediatype": "image/jpeg",
        "metahash": "1e209ce5052a03004657d8657167f53812718e9426d85b4cdd5106ef3d87412e6f64",
        "mode": "image",
        "name": "Concentrated Cat",
        "thumbnail": "data:image/webp;base64,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",
        "width": 200,
    }


def test_code_meta_image(jpg_file):
    assert idk.code_meta(jpg_file).dict() == {
        "iscc": "ISCC:AAAWRY3VY6R5SNV4",
        "name": "Concentrated Cat",
        "creator": "Some Cat Lover",
        "width": 200,
        "height": 133,
        "metahash": "1e209ce5052a03004657d8657167f53812718e9426d85b4cdd5106ef3d87412e6f64",
    }


def test_code_meta_image_no_meta(bmp_file):
    assert idk.code_meta(bmp_file).dict() == {
        "iscc": "ISCC:AAA374FA7VF3FWZQ",
        "name": "img",
        "width": 200,
        "height": 133,
        "metahash": "1e20bff0a0fd4bb2db301741c4c9cbfced1085e2051e6009edb12b004330fa7f5111",
    }


def test_code_meta_raises():
    fp = texts()[0].as_posix()
    with pytest.raises(ValueError):
        idk.code_meta(fp)


def test_code_content(jpg_file):
    assert idk.code_content(jpg_file).dict() == {
        "creator": "Some Cat Lover",
        "height": 133,
        "iscc": "ISCC:EEA4GQZQTY6J5DTH",
        "mediatype": "image/jpeg",
        "mode": "image",
        "name": "Concentrated Cat",
        "thumbnail": "data:image/webp;base64,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",
        "width": 200,
    }


def test_code_content_raises(doc_file):
    with pytest.raises(ValueError):
        idk.code_content(doc_file)


def test_code_image(jpg_file):
    assert idk.code_image(jpg_file) == {
        "creator": "Some Cat Lover",
        "height": 133,
        "iscc": "ISCC:EEA4GQZQTY6J5DTH",
        "name": "Concentrated Cat",
        "thumbnail": "data:image/webp;base64,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",
        "width": 200,
    }


def test_code_data(png_file):
    assert idk.code_data(png_file) == {"iscc": "ISCC:GAAXUI3LCN7D7VDE"}


def test_code_instance(png_file):
    assert idk.code_instance(png_file).dict() == {
        "iscc": "ISCC:IAA75OC7C4E7KHV7",
        "filesize": 54595,
        "datahash": "1e20feb85f1709f51ebf31c2feab2092a61826da36cc79eddc4cb04800b47db146a6",
    }
