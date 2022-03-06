# -*- coding: utf-8 -*-
from PIL.Image import Image

import iscc_sdk as idk
from iscc_schema.schema import ISCC
from iscc_samples import images


fp = images("jpg")[0].as_posix()
meta = ISCC.construct(name="Hello", description="Wörld", meta="somestring")


def test_image_meta_extract_jpg(jpg_file):
    assert idk.image_meta_extract(jpg_file) == {
        "creator": "Some Cat Lover",
        "name": "Concentrated Cat",
    }


def test_image_meta_extract_png(png_file):
    assert idk.image_meta_extract(png_file) == {
        "creator": "Another Cat Lover",
        "name": "Concentrated Cat PNG",
    }


def test_image_meta_delete_jpg(jpg_file):
    idk.image_meta_delete(jpg_file)
    assert idk.image_meta_extract(jpg_file) == {}


def test_image_meta_delete_png(png_file):
    idk.image_meta_delete(png_file)
    assert idk.image_meta_extract(png_file) == {}


def test_image_meta_embed_jpg(jpg_file):
    assert idk.image_meta_embed(jpg_file, meta) is None
    assert idk.image_meta_extract(jpg_file) == meta.dict(exclude_unset=True)


def test_image_meta_embed_png(png_file):
    assert idk.image_meta_embed(png_file, meta) is None
    assert idk.image_meta_extract(png_file) == meta.dict(exclude_unset=True)


def test_image_thumbnail():
    thumb = idk.image_thumbnail(fp)
    assert isinstance(thumb, Image)


def test_image_to_data_url():
    img = idk.image_thumbnail(fp)
    durl = idk.image_to_data_url(img)
    assert durl.startswith("data:image/webp;base64,UklGRvAHAABXRUJQVlA4IOQHAABQJQCdASqAAFUAPrVMnku")
    assert durl.endswith("XUVIqfr+x9Igy/FehT0vBRAhNP+u6v9LEZRqfbxADwwWRSEk6Io4VSGX5LpRVqMLCG+eYAAA")


def test_image_normalize():
    img = idk.image_thumbnail(fp)
    pixels = list(idk.image_normalize(img))
    assert pixels[:14] == [24, 17, 14, 14, 24, 79, 91, 91, 106, 66, 110, 100, 99, 92]
    assert pixels[-14:] == [67, 65, 70, 59, 64, 65, 65, 64, 61, 65, 53, 61, 49, 51]
