# -*- coding: utf-8 -*-
import pytest
from PIL.Image import DecompressionBombError

import iscc_sdk as idk
from iscc_samples import images

fp = images("jpg")[0].as_posix()


def test_image_max_pixels_small():
    idk.sdk_opts.image_max_pixels = 10
    with pytest.raises(DecompressionBombError):
        idk.code_image(fp)


def test_image_max_pixels_None():
    idk.sdk_opts.image_max_pixels = None
    r = idk.code_image(fp)
    assert r.iscc == "ISCC:EEA4GQZQTY6J5DTH"
