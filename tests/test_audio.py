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
        "duration": 15,
    }


def test_audio_meta_extract_concurrent(mp3_file):
    with open(mp3_file, "rb") as infile:
        data = infile.read(64)
        assert idk.audio_meta_extract(mp3_file) == {
            "name": "Belly Button",
            "duration": 15,
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
        "duration": 15,
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
        "duration": 15,
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
        "duration": 15,
        "iscc": "ISCC:EIAWUJFCEZZOJYVD",
        "name": "Belly Button",
    }


def test_code_audio_wav(wav_file):
    assert idk.code_audio(wav_file).dict() == {
        "duration": 15,
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
    meta = idk.code_audio(mp3_cover)
    assert meta.dict() == {
        "creator": "Test Artist",
        "duration": 15,
        "iscc": "ISCC:EIAWUJFCEZZOJYVD",
        "name": "Belly Button",
        "thumbnail": "data:image/webp;base64,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",
    }


def test_audio_embed_title(mp3_cover):
    new_file = idk.embed_metadata(mp3_cover, idk.IsccMeta(name="Embedded Title"))
    meta = idk.extract_metadata(new_file)
    assert meta.dict() == {"creator": "Test Artist", "duration": 15, "name": "Embedded Title"}


def test_code_audio_metadata_extraction_disabled(mp3_cover):
    idk.sdk_opts.extract_metadata = False
    meta = idk.code_audio(mp3_cover)
    assert meta.dict() == {"iscc": "ISCC:EIAWUJFCEZZOJYVD"}
    idk.sdk_opts.extract_metadata = True
