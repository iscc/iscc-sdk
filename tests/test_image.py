# -*- coding: utf-8 -*-
import iscc_sdk as idk
from iscc_schema.schema import ISCC
from iscc_samples import images


fp = images("jpg")[0].as_posix()
meta = ISCC.construct(name="Hello", description="Wörld", meta="somestring")


def test_image_meta_extract():
    assert idk.image_meta_extract(images("png")[0].as_posix()) == {
        "creator": "Another Cat Lover",
        "name": "Concentrated Cat PNG",
    }


def test_image_meta_delete():
    idk.image_meta_delete(fp)
    assert idk.image_meta_extract(fp) == {}


def test_image_meta_embed():
    idk.image_meta_embed(fp, meta)
    assert idk.image_meta_extract(fp) == meta.dict(exclude_unset=True)
