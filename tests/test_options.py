# -*- coding: utf-8 -*-
import pytest
from PIL import Image
import iscc_sdk as idk
from iscc_samples import images


fp = images("jpg")[0].as_posix()


def test_image_max_pixels_small(monkeypatch):
    monkeypatch.setattr(idk.sdk_opts, "image_max_pixels", 10)
    with pytest.raises(Image.DecompressionBombError):
        idk.code_image(fp)


def test_image_max_pixels_None(monkeypatch):
    monkeypatch.setattr(idk.sdk_opts, "image_max_pixels", None)
    r = idk.code_image(fp)
    assert r.iscc == "ISCC:EEA4GQZQTY6J5DTH"


def test_sdk_options_default():
    assert isinstance(idk.sdk_opts, idk.SdkOptions)
    assert idk.sdk_opts.granular is False
    assert idk.sdk_opts.extract_meta is True
    assert idk.sdk_opts.create_thumb is True


def test_sdk_options_override():
    new_opts = idk.sdk_opts.override({"granular": True, "extract_meta": False})
    assert new_opts.granular is True
    assert new_opts.extract_meta is False
    assert new_opts.create_thumb is True  # Unchanged
    assert idk.sdk_opts.granular is False  # Original instance unchanged
    assert idk.sdk_opts.extract_meta is True  # Original instance unchanged


def test_sdk_options_override_invalid_field():
    with pytest.raises(ValueError, match="Invalid field: invalid_field"):
        idk.sdk_opts.override({"invalid_field": True})


def test_sdk_options_image_max_pixels():
    original_max_pixels = Image.MAX_IMAGE_PIXELS
    new_opts = idk.SdkOptions(image_max_pixels=1000000)
    assert new_opts.image_max_pixels == 1000000
    assert Image.MAX_IMAGE_PIXELS == 1000000

    # Reset to original value
    Image.MAX_IMAGE_PIXELS = original_max_pixels


def test_sdk_options_override_empty():
    new_opts = idk.sdk_opts.override()
    assert new_opts.granular == idk.sdk_opts.granular
    assert new_opts.extract_meta == idk.sdk_opts.extract_meta
    assert new_opts.create_thumb == idk.sdk_opts.create_thumb


def test_sdk_options_override_multiple_fields():
    new_opts = idk.sdk_opts.override(
        {
            "granular": True,
            "extract_meta": False,
            "create_thumb": False,
            "image_max_pixels": 500000,
        }
    )
    assert new_opts.granular is True
    assert new_opts.extract_meta is False
    assert new_opts.create_thumb is False
    assert new_opts.image_max_pixels == 500000
    assert Image.MAX_IMAGE_PIXELS == 500000

    # Reset Image.MAX_IMAGE_PIXELS
    Image.MAX_IMAGE_PIXELS = idk.sdk_opts.image_max_pixels
