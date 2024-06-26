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


def test_video_thumbnail_fail(docx_file):
    thumb = idk.video_thumbnail(docx_file)
    assert thumb is None


def test_video_mp7sig_extract(mp4_file):
    sig = idk.video_mp7sig_extract(mp4_file)
    assert sig[-32:].hex() == "9ef43526febb8d3e674975584ad6812ccc144cba28b3e134cd173888449cf51e"


def test_video_mp7sig_extract_scenes_compat(mp4_file):
    sig, scenes = idk.video_mp7sig_extract_scenes(mp4_file)
    assert sig[-32:].hex() == "9ef43526febb8d3e674975584ad6812ccc144cba28b3e134cd173888449cf51e"


def test_video_mp7sig_extract_scenes_detected(mp4_file):
    _, scenes = idk.video_mp7sig_extract_scenes(mp4_file, scene_limit=0.2)
    assert scenes == [7.625, 10.125, 15.208, 36.0, 38.458, 39.958, 46.625, 60.0]


def test_video_parse_scenes_empty():
    assert idk.video_parse_scenes(" ") == []


def test_video_features_extract(mp4_file):
    features = idk.video_features_extract(mp4_file)
    assert features[0][:20] == (0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0)


def test_video_features_extract_store(mp4_file):
    idk.sdk_opts.video_store_mp7sig = True
    idk.video_features_extract(mp4_file)
    assert Path(mp4_file + ".iscc.mp7sig").exists()
    idk.sdk_opts.video_store_mp7sig = True


def test_code_video_nometa_nothumb(mp4_file):
    idk.sdk_opts.extract_metadata = False
    idk.sdk_opts.create_thumbnail = False
    meta = idk.code_video(mp4_file)
    assert meta.dict() == {"iscc": "ISCC:EMAV4DUD6QORW4X4"}
    idk.sdk_opts.extract_metadata = True
    idk.sdk_opts.create_thumbnail = True


def test_code_video_granular_scenes(mp4_file):
    idk.sdk_opts.granular = True
    idk.sdk_opts.video_scene_limit = 0.2
    idk.sdk_opts.create_thumbnail = False
    idk.sdk_opts.extract_metadata = True
    result = idk.code_video(mp4_file).dict()
    assert result == {
        "iscc": "ISCC:EMAV4DUD6QORW4X4",
        "name": "Kali by Anokato - Spiral Sessions 2019",
        "features": {
            "kind": "video",
            "version": 0,
            "sizes": [7.625, 2.5, 5.083, 20.792, 2.458, 1.5, 6.667],
            "features": [
                "XxqT9x1acvw",
                "HEqSawAW8oQ",
                "VA7Q9A0esuw",
                "Xg4H9H1S8vU",
                "l06Qp9wbcow",
                "UWAQkpxZMqg",
                "HloAnYYVUqU",
            ],
        },
    }


def test_code_iscc_video_granular(mp4_file):
    idk.sdk_opts.granular = True
    idk.sdk_opts.video_scene_limit = 0.2
    idk.sdk_opts.create_thumbnail = False
    idk.sdk_opts.extract_metadata = True
    result = idk.code_iscc(mp4_file).dict()
    assert result == {
        "@type": "VideoObject",
        "iscc": "ISCC:KMCV6UK6BSXJ3I4GLYHIH5A5DNZPYBWQO33FNHPQFOOUCLLW3HKRNUA",
        "name": "Kali by Anokato - Spiral Sessions 2019",
        "mode": "video",
        "mediatype": "video/mp4",
        "filename": "video.mp4",
        "filesize": 2161914,
        "metahash": "1e2096c0a53475a186ce37622aba7ba70651fc62cc8150f59eee6d17dc16d9bfbf25",
        "datahash": "1e209d412d76d9d516d07bb60f1ab3c1a5c1b176ed4f1cec94c96222a5d013ec3e38",
        "features": {
            "kind": "video",
            "version": 0,
            "features": [
                "XxqT9x1acvw",
                "HEqSawAW8oQ",
                "VA7Q9A0esuw",
                "Xg4H9H1S8vU",
                "l06Qp9wbcow",
                "UWAQkpxZMqg",
                "HloAnYYVUqU",
            ],
            "sizes": [7.625, 2.5, 5.083, 20.792, 2.458, 1.5, 6.667],
        },
    }


def test_code_iscc_video_granular_no_scenes(mp4_file):
    idk.sdk_opts.granular = True
    idk.sdk_opts.video_scene_limit = 0.8
    idk.sdk_opts.create_thumbnail = False
    idk.sdk_opts.extract_metadata = True
    result = idk.code_iscc(mp4_file).dict()
    assert result == {
        "@type": "VideoObject",
        "iscc": "ISCC:KMCV6UK6BSXJ3I4GLYHIH5A5DNZPYBWQO33FNHPQFOOUCLLW3HKRNUA",
        "name": "Kali by Anokato - Spiral Sessions 2019",
        "mode": "video",
        "mediatype": "video/mp4",
        "filename": "video.mp4",
        "filesize": 2161914,
        "metahash": "1e2096c0a53475a186ce37622aba7ba70651fc62cc8150f59eee6d17dc16d9bfbf25",
        "datahash": "1e209d412d76d9d516d07bb60f1ab3c1a5c1b176ed4f1cec94c96222a5d013ec3e38",
        "features": {
            "kind": "video",
            "version": 0,
            "features": [
                "Xg6D9B0bcvw",
            ],
            "sizes": [59.8],
        },
    }
