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
    assert durl.startswith("data:image/webp;base64,UklGRsoFAABXRUJQVlA4IL4FAADwIQCdASqAAFUAPxF2sFK")


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
    assert idk.image_meta_extract(new_file)["name"] == long_name
    assert idk.code_iscc(new_file).name == long_name[:128]


def test_embed_metadata_non_uri(jpg_file):
    meta = idk.image_meta_extract(jpg_file)
    assert meta == {"height": 133, "width": 200}
    new_file = idk.image_meta_embed(jpg_file, IsccMeta.construct(license="Hello World"))
    assert idk.image_meta_extract(new_file) == {
        "height": 133,
        "license": "Hello World",
        "width": 200,
    }


def test_embed_identifier(jpg_file):
    """Test embedding and extracting the identifier field."""
    identifier = "ISCC:KACYPXW46UOGYH3C"
    meta = IsccMeta.construct(identifier=identifier)
    new_file = idk.image_meta_embed(jpg_file, meta)
    extracted = idk.image_meta_extract(new_file)
    assert extracted["identifier"] == identifier
    os.remove(new_file)


def test_clean_xmp_value():
    """Test the _clean_xmp_value function that processes XMP language qualifiers."""
    # Test with language qualifier
    value = 'lang="x-default" Some Value'
    assert idk.image._clean_xmp_value(value) == "Some Value"

    # Test without language qualifier
    value = "Some Value"
    assert idk.image._clean_xmp_value(value) == "Some Value"

    # Test with incomplete qualifier (edge case)
    value = 'lang="x-default'
    assert idk.image._clean_xmp_value(value) == 'lang="x-default'


def test_process_metadata_to_string():
    """Test that non-string values with to_string method are properly converted."""

    # Create a simple class that simulates an exiv2 metadata value with to_string method
    class MockToString:
        def to_string(self):
            return "converted string value"

    # Create a mock datum that simulates the exiv2 metadata datum structure
    class MockDatum:
        def __init__(self, key, value):
            self._key = key
            self._value = value

        def key(self):
            return self._key

        @property
        def value(self):
            return self._value

    # Create test data
    mock_value = MockToString()
    mock_datum = MockDatum("Test.Key", mock_value)

    # Call the function with our mock data
    result = idk.image._process_metadata([mock_datum])

    # Verify the result
    assert result["Test.Key"] == "converted string value"


def test_code_image_nometa_nothumb(jpg_file):
    idk.sdk_opts.extract_metadata = False
    idk.sdk_opts.create_thumbnail = False
    meta = idk.code_image(jpg_file)
    assert meta.dict() == {"iscc": "ISCC:EEA4GQZQTY6J5DTH"}
    idk.sdk_opts.extract_metadata = True
    idk.sdk_opts.create_thumbnail = True
