# -*- coding: utf-8 -*-
import os.path

from PIL import Image

import iscc_sdk as idk
from iscc_schema import IsccMeta
from iscc_samples import images


fp = images("jpg")[0].as_posix()
meta = IsccMeta.construct(
    name="Hello",
    description="Wörld",
    meta="somestring",
    license="https://example.com/license",
    acquire="https://example.com/buy",
)


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
        "height": 133,
        "name": "Concentrated Cat",
        "width": 200,
    }


def test_image_meta_extract_png(png_file):
    assert idk.image_meta_extract(png_file) == {
        "creator": "Another Cat Lover",
        "height": 133,
        "name": "Concentrated Cat PNG",
        "width": 200,
    }


def test_image_meta_delete_jpg(jpg_file):
    idk.image_meta_delete(jpg_file)
    assert idk.image_meta_extract(jpg_file) == {"height": 133, "width": 200}


def test_image_meta_delete_png(png_file):
    idk.image_meta_delete(png_file)
    assert idk.image_meta_extract(png_file) == {"height": 133, "width": 200}


def test_image_meta_embed_jpg(jpg_file):
    new_file = idk.image_meta_embed(jpg_file, meta)
    assert os.path.exists(new_file)
    assert idk.image_meta_extract(new_file) == {
        "acquire": "https://example.com/buy",
        "description": "Wörld",
        "height": 133,
        "license": "https://example.com/license",
        "meta": "somestring",
        "name": "Hello",
        "width": 200,
    }
    os.remove(new_file)


def test_image_meta_embed_png(png_file):
    new_file = idk.image_meta_embed(png_file, meta)
    assert os.path.exists(new_file)
    assert idk.image_meta_extract(new_file) == {
        "acquire": "https://example.com/buy",
        "description": "Wörld",
        "height": 133,
        "license": "https://example.com/license",
        "meta": "somestring",
        "name": "Hello",
        "width": 200,
    }
    os.remove(new_file)


def test_image_thumbnail():
    thumb = idk.image_thumbnail(fp)
    assert isinstance(thumb, Image.Image)


def test_image_to_data_url():
    img = idk.image_thumbnail(fp)
    durl = idk.image_to_data_url(img)
    assert durl.startswith("data:image/webp;base64,UklGRvAHAABXRUJQVlA4IOQHAABQJQCdASqAAFUAPrVMnku")
    assert durl.endswith("XUVIqfr+x9Igy/FehT0vBRAhNP+u6v9LEZRqfbxADwwWRSEk6Io4VSGX5LpRVqMLCG+eYAAA")


def test_embed_rights_and_creator(jpg_file):
    meta = IsccMeta.construct(
        creator="Some Creatör Name",
        rights="Some Cäpyright notice",
    )
    new_file = idk.image_meta_embed(jpg_file, meta)
    assert idk.image_meta_extract(new_file) == {
        "creator": "Some Creatör Name",
        "height": 133,
        "rights": "Some Cäpyright notice",
        "width": 200,
    }
    os.remove(new_file)


def test_extract_name_above_128(jpg_file):
    long_name = "a" * 130
    meta = IsccMeta.construct(name=long_name)
    new_file = idk.image_meta_embed(jpg_file, meta)
    # assert isinstance(new_file, str)
    assert idk.image_meta_extract(new_file) == {
        "height": 133,
        "name": long_name,
        "width": 200,
    }
    assert idk.code_iscc(new_file).dict() == {
        "@type": "ImageObject",
        "datahash": "1e2098e44c98c9cb45ba94b2fd497180e210c51d6d7ed0b7a73128c9751562af2837",
        "filename": "img.jpg",
        "filesize": 28796,
        "height": 133,
        "iscc": "ISCC:KECTBQHZY2QWP7BKYNBTBHR4T2HGP3MLVE64D3M36CMOITEYZHFULOQ",
        "mediatype": "image/jpeg",
        "metahash": "1e200753df896d00f20c247f7e8c8977bb84d42f57532a5cc30d8f2ea035c9ce5757",
        "mode": "image",
        "name": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "thumbnail": "data:image/webp;base64,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",
        "width": 200,
    }


def test_embed_metadata_non_uri(jpg_file):
    meta = idk.image_meta_extract(jpg_file)
    assert meta == {"height": 133, "width": 200}
    new_file = idk.image_meta_embed(jpg_file, IsccMeta.construct(license="Hello World"))
    assert idk.image_meta_extract(new_file) == {
        "height": 133,
        "license": "Hello World",
        "width": 200,
    }


def test_code_image_no_metadata(jpg_file):
    idk.sdk_opts.extract_metadata = False
    meta = idk.code_image(jpg_file)
    assert meta.dict() == {"iscc": "ISCC:EEA4GQZQTY6J5DTH"}
    idk.sdk_opts.extract_metadata = True
