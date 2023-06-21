# -*- coding: utf-8 -*-
import os
from pathlib import Path

from PIL import Image
import iscc_sdk as idk


meta = idk.IsccMeta(
    name="Hello",
    description="Wörld",
    meta="somestring",
    creator="The Creator",
    license="https://example.com/license",
    acquire="https://example.com/buy",
    rights="Copyright Notice",
)


def test_video_metadata_extract_mp4(mp4_file):
    assert idk.video_meta_extract(mp4_file) == {"name": "Kali by Anokato - Spiral Sessions 2019"}


def test_video_metadata_embed_mp4(mp4_file):
    new_file = idk.video_meta_embed(mp4_file, meta)
    assert idk.video_meta_extract(new_file) == {
        "name": "Hello",
        "description": "Wörld",
        "meta": "somestring",
        "creator": "The Creator",
        "license": "https://example.com/license",
        "acquire": "https://example.com/buy",
        "rights": "Copyright Notice",
    }
    os.remove(new_file)


def test_video_metadata_extract_mov(mov_file):
    assert idk.video_meta_extract(mov_file) == {"name": "Kali by Anokato - Spiral Sessions 2019"}


def test_video_metadata_embed_mov(mov_file):
    new_file = idk.video_meta_embed(mov_file, meta)
    assert idk.video_meta_extract(new_file) == {
        "name": "Hello",
        "description": "Wörld",
        "meta": "somestring",
        "creator": "The Creator",
        "license": "https://example.com/license",
        "acquire": "https://example.com/buy",
        "rights": "Copyright Notice",
    }
    os.remove(new_file)


def test_video_metadata_escaping(mp4_file):
    meta = idk.IsccMeta(
        name="Some # Name",
        description="Multi\nLine\n\nDescription with ; and other = crazy characters\n",
    )
    new_file = idk.video_meta_embed(mp4_file, meta)
    assert idk.video_meta_extract(new_file) == dict(
        name="Some # Name",
        description="Multi\nLine\n\nDescription with ; and other = crazy characters",
    )
    os.remove(new_file)


def test_video_thumbnail(mp4_file):
    thumb = idk.video_thumbnail(mp4_file)
    assert isinstance(thumb, Image.Image)


def test_video_thumbnail_fail(ogv_file):
    thumb = idk.video_thumbnail(ogv_file)
    assert thumb is None


def test_video_mp7sig_extract(mp4_file):
    sig = idk.video_mp7sig_extract(mp4_file)
    assert sig[-32:].hex() == "9ef43526febb8d3e674975584ad6812ccc144cba28b3e134cd173888449cf51e"


def test_video_features_extract(mp4_file):
    features = idk.video_features_extract(mp4_file)
    assert features[0][:20] == (0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0)


def test_video_features_extract_store(mp4_file):
    idk.sdk_opts.video_store_mp7sig = True
    idk.video_features_extract(mp4_file)
    assert Path(mp4_file + ".iscc.mp7sig").exists()
    idk.sdk_opts.video_store_mp7sig = True


def test_code_video_no_meta_extract(mp4_file):
    idk.sdk_opts.extract_metadata = False
    meta = idk.code_video(mp4_file)
    assert meta.dict() == {"iscc": "ISCC:EMAV4DUD6QORW4X4"}
    idk.sdk_opts.extract_metadata = True
