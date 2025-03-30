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
    meta = idk.code_audio(mp3_cover)
    assert meta.dict() == {
        "creator": "Test Artist",
        "duration": 15.543,
        "iscc": "ISCC:EIAWUJFCEZZOJYVD",
        "name": "Belly Button",
        "thumbnail": "data:image/avif;base64,AAAAIGZ0eXBhdmlmAAAAAGF2aWZtaWYxbWlhZk1BMUIAAADrbWV0YQAAAAAAAAAhaGRscgAAAAAAAAAAcGljdAAAAAAAAAAAAAAAAAAAAAAOcGl0bQAAAAAAAQAAAB5pbG9jAAAAAEQAAAEAAQAAAAEAAAETAAADuQAAAChpaW5mAAAAAAABAAAAGmluZmUCAAAAAAEAAGF2MDFDb2xvcgAAAABqaXBycAAAAEtpcGNvAAAAFGlzcGUAAAAAAAAAgAAAAIAAAAAQcGl4aQAAAAADCAgIAAAADGF2MUOBAAwAAAAAE2NvbHJuY2x4AAEADQAGgAAAABdpcG1hAAAAAAAAAAEAAQQBAoMEAAADwW1kYXQSAAoJGBm//2CAhoNCMqkHEsAGmmmhQNxqCFrKmqg8qDKE8K/dAf6p7hRlQ+tJIC3xS9+lzDK0Gjv41/NNBnEUefU6Z6URjqAjBDFoag3/czyVCW8VXU/9WsMLPn2tUXh7J5nyBOFL9oFbia6LGvKHJ4GUymRwy000E9kvy4dwwLsX/kzmUfL/J8DzxwUROAWiSuxY93UzMiwlqgoThE2wbIM0m9EajHC/tryZClkmhb3VqAKXcwlCZ14+0DQSVwjFjO/4H1UUz+0yekQoTsOQ/1p+znWJ3f0fxEuzH58FXwb1ZSqXy5lwmjIfJbMWXd4dYYMoeuK7Ww4v7xIvfUToaNr2V3aJhLW2vtYIFGichz5sYArAxOsvhbGhvtdZAyFIkMQrN/LUNjoSFU82kHZ7fsiOds1HSSNUcAqQB26HFRLE33f4G0jbmhYapk1inRCTDjOun7l8y/6PbYXz1KqY0ipnpnhY/LiddvU2Lw/a3IHRKoDrKkQX+PYMN80wSorine/UW+lO0rDzV9Xb8bxinqHBnAE+FB3OClwODLHNljOwa2tkJXda81YwjvYt0F35S3iVvKwPp3qF3x/szQLsrO7DOgHR9caXwSwp0r0jAlApqcs4Ga+/5F+LVCyCMelLU0pajOVQXkBf9CxeC76DdTlFZiYTzuPOLr+53kjKNityM8tZIzKzlSrgj6FZW3VvFIfONgSlxOlOQsMGhn4Oyu9T5alW2Xv4BLERyMPaS5ZEyT/PK3d9f7wIQIcz0HDFvx/wbyUv20O2mNhF8N7MEWbTnn4wfiaF04vXk0Ki2JkIwLZsFjvN/laG61SDgdsNYLYZ11csOIgMtgIeiPkaPPB5t+Ddk+QBcf33IKV2IvZ+zkQ/2ahNIQspkHhfH8Hj3Mqb60XaPqtVTRhHRExPEYQ5i0noPpZd8/VW3tYuwXV5AIoiJO0OSg+YREZiYWtqreXLcWLcgk7YWPh85H/S7WxJ9LO2ios+b1sU3RoWga1n3qY5XAA6/8X+A/Kfhk6X+Y2sLWdeeFud62RiPQEUkHDsBHiq9R+lLTXDIggwhQlMHQbLgdXLN26tXELdtp7C7TyOjwEdCJDznZndEyxrduQqhWe0mwH0ZhdOBugNqCpb1a/fpWO2vdVBkxAEpr6dcKLDgrgiPkc7KjmSQms9zodPdLv+Dd6AMA7uA41x4y1G+TlEx9HPbG5/646vxzjIEflks9z3B6quEEtsEGHLf3kV/dIo1yDO4ad9f4wpPi7OmV6uVPMAgA==",
    }


def test_audio_embed_title(mp3_cover):
    new_file = idk.embed_metadata(mp3_cover, idk.IsccMeta(name="Embedded Title"))
    meta = idk.extract_metadata(new_file)
    assert meta.dict() == {"creator": "Test Artist", "duration": 15.543, "name": "Embedded Title"}


def test_code_audio_metadata_meta_thumb_disabled(mp3_cover):
    idk.sdk_opts.extract_metadata = False
    idk.sdk_opts.create_thumbnail = False
    meta = idk.code_audio(mp3_cover)
    assert meta.dict() == {"iscc": "ISCC:EIAWUJFCEZZOJYVD"}
    idk.sdk_opts.extract_metadata = True
    idk.sdk_opts.create_thumbnail = True
