# -*- coding: utf-8 -*-
from PIL import Image

import iscc_sdk as idk
from iscc_schema.schema import ISCC
from iscc_samples import images


fp = images("jpg")[0].as_posix()
meta = ISCC.construct(name="Hello", description="Wörld", meta="somestring")


def test_image_normalize_png(png_obj):
    pixels = list(idk.image_normalize(png_obj))
    assert pixels[:14] == [25, 18, 14, 15, 25, 80, 92, 92, 106, 68, 110, 100, 99, 93]
    assert pixels[-14:] == [68, 65, 71, 60, 65, 65, 66, 65, 61, 65, 54, 62, 50, 52]


def test_image_normalize_png_alpha(png_obj_alpha):
    pixels = list(idk.image_normalize(png_obj_alpha))
    assert pixels[:14] == [255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255]
    assert pixels[-14:] == [255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255]


def test_image_normalize_jpg(jpg_obj):
    pixels = list(idk.image_normalize(jpg_obj))
    assert pixels[:14] == [25, 18, 14, 15, 25, 79, 92, 92, 106, 68, 110, 101, 99, 93]
    assert pixels[-14:] == [67, 65, 71, 59, 65, 65, 66, 65, 61, 66, 54, 62, 50, 52]


def test_image_exif_transpose(png_obj):
    result = idk.image_exif_transpose(png_obj)
    assert isinstance(result, Image.Image)


def test_image_fill_transparency(png_obj_alpha):
    result = idk.image_fill_transparency(png_obj_alpha)
    assert isinstance(result, Image.Image)


def test_image_trim_border(jpg_obj, png_obj_alpha):
    assert jpg_obj.size == (200, 133)
    result = idk.image_trim_border(jpg_obj)
    assert result.size == (200, 133)
    assert png_obj_alpha.size == (100, 100)
    result = idk.image_trim_border(png_obj_alpha)
    assert result.size == (51, 51)


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
    assert isinstance(thumb, Image.Image)


def test_image_to_data_url():
    img = idk.image_thumbnail(fp)
    durl = idk.image_to_data_url(img)
    assert durl.startswith("data:image/webp;base64,UklGRvAHAABXRUJQVlA4IOQHAABQJQCdASqAAFUAPrVMnku")
    assert durl.endswith("XUVIqfr+x9Igy/FehT0vBRAhNP+u6v9LEZRqfbxADwwWRSEk6Io4VSGX5LpRVqMLCG+eYAAA")
