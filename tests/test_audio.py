# -*- coding: utf-8 -*-
import os.path
from PIL.Image import Image
import iscc_sdk as idk
import iscc_samples as iss


meta = idk.IsccMeta.construct(
    name="Hello",
    description="Wörld",
    meta="somestring",
    license="https://example.com/license",
    acquire="https://example.com/buy",
)


def test_audio_meta_extract(mp3_file):
    assert idk.audio_meta_extract(mp3_file) == {
        "name": "Belly Button",
        "duration": 15.543,
    }


def test_audio_meta_extract_concurrent(mp3_file):
    with open(mp3_file, "rb") as infile:
        data = infile.read(64)
        assert idk.audio_meta_extract(mp3_file) == {
            "name": "Belly Button",
            "duration": 15.543,
        }


def test_audio_meta_extract_all():
    for fp in iss.audios():
        metadata = idk.audio_meta_extract(fp.as_posix())
        assert isinstance(metadata, dict)


def test_audio_meta_embed_mp3(mp3_file):
    new_file = idk.audio_meta_embed(mp3_file, meta)
    assert os.path.exists(new_file)
    assert idk.audio_meta_extract(new_file) == {
        "acquire": "https://example.com/buy",
        "description": "Wörld",
        "duration": 15.543,
        "license": "https://example.com/license",
        "meta": "somestring",
        "name": "Hello",
    }
    os.remove(new_file)


def test_audio_meta_embed_wav(wav_file):
    new_file = idk.audio_meta_embed(wav_file, meta)
    assert os.path.exists(new_file)
    assert idk.audio_meta_extract(new_file) == {
        "acquire": "https://example.com/buy",
        "description": "Wörld",
        "duration": 15.503,
        "license": "https://example.com/license",
        "meta": "somestring",
        "name": "Hello",
    }
    os.remove(new_file)


def test_audio_extract_features(mp3_file):
    assert idk.audio_features_extract(mp3_file) == {
        "duration": 15.54,
        "fingerprint": [
            684003877,
            683946551,
            1749295639,
            2017796679,
            2026256086,
            2022066918,
            2022001639,
            2021968035,
            2038741139,
            2059709571,
            503750851,
            369541315,
            320225426,
            289292450,
            830368930,
            838789539,
            1940835201,
            1928186752,
            1651297920,
            1651283600,
            1650959072,
            1655022116,
            1722069540,
            1726259749,
            1713694254,
            1847914286,
            1847912494,
            1780832302,
            -362410962,
            -352973810,
            1809196111,
            1770397775,
            1753686797,
            683942429,
            943989277,
            943989255,
            944121430,
            952503910,
            948374246,
            948717799,
            1485621411,
            462203011,
            508470403,
            370053251,
            303988867,
            322879651,
            322892963,
            862907811,
            1928256417,
            1928317841,
            1651297152,
            1647091344,
            1650827936,
            1659216416,
            1722069540,
            1726263844,
            1717887533,
            1713696302,
            1847912494,
            1847883822,
            -366540754,
            -345633778,
            -336184242,
            1771447375,
            1753620815,
            1757684255,
            675553815,
            943989255,
            944120390,
            952508006,
            948308582,
            948718050,
            411879650,
            428648578,
            516861059,
            370057347,
            303988865,
            306086033,
            306086049,
            841919649,
            846133665,
            1919929264,
            1647168400,
            1647101584,
            1650827936,
            1659216484,
            1671733796,
            1738838588,
            1717887517,
            1713696302,
            1847913774,
            1847879726,
            1780960302,
            -362410978,
            -336196594,
            1775641678,
            1770397775,
            1753555743,
            683942429,
            943989271,
            944185926,
            2026255094,
            2022051494,
            2021919654,
        ],
    }


def test_code_audio_mp3(mp3_file):
    assert idk.code_audio(mp3_file).dict() == {
        "duration": 15.543,
        "iscc": "ISCC:EIAWUJFCEZZOJYVD",
        "name": "Belly Button",
    }


def test_code_audio_wav(wav_file):
    assert idk.code_audio(wav_file).dict() == {
        "duration": 15.503,
        "iscc": "ISCC:EIAWUJFCEZZOJYVD",
        "name": "Belly Button!",
    }


def test_audio_thumbnail_none(mp3_file):
    img = idk.audio_thumbnail(mp3_file)
    assert img is None


def test_audio_thumbnail_found(mp3_cover):
    img = idk.audio_thumbnail(mp3_cover)
    assert isinstance(img, Image)


def test_audio_thumbnail_via_code_audio(mp3_cover):
    meta = idk.code_audio(mp3_cover).dict()
    assert meta == {
        "creator": "Test Artist",
        "duration": 15.543,
        "iscc": "ISCC:EIAWUJFCEZZOJYVD",
        "name": "Belly Button",
        "thumbnail": "data:image/webp;base64,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",
    }


def test_audio_embed_title(mp3_cover):
    new_file = idk.embed_metadata(mp3_cover, idk.IsccMeta(name="Embedded Title"))
    meta = idk.extract_metadata(new_file)
    assert meta.dict() == {"creator": "Test Artist", "duration": 15.543, "name": "Embedded Title"}


def test_code_audio_metadata_meta_thumb_disabled(mp3_cover, monkeypatch):
    monkeypatch.setattr(idk.sdk_opts, "extract_meta", False)
    monkeypatch.setattr(idk.sdk_opts, "create_thumb", False)
    meta = idk.code_audio(mp3_cover)
    assert meta.dict() == {"iscc": "ISCC:EIAWUJFCEZZOJYVD"}
