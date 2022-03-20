# -*- coding: utf-8 -*-
import iscc_sdk as idk
import iscc_schema as iss

meta = iss.IsccMeta(
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
