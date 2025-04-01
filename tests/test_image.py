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


def test_code_image_nometa_nothumb(jpg_file, monkeypatch):
    monkeypatch.setattr(idk.sdk_opts, "extract_meta", False)
    monkeypatch.setattr(idk.sdk_opts, "create_thumb", False)
    meta = idk.code_image(jpg_file)
    assert meta.dict() == {"iscc": "ISCC:EEA4GQZQTY6J5DTH"}


def test_thumbnail_data_url_jpeg(jpg_file, monkeypatch):
    monkeypatch.setattr(idk.sdk_opts, "image_thumbnail_format", "JPEG")
    img = idk.thumbnail(jpg_file)
    img = idk.image_strip_metadata(img)
    durl = idk.image_to_data_url(img)
    assert (
        durl
        == "data:image/jpeg;base64,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"
    )


def test_thumbnail_data_url_webp(jpg_file, monkeypatch):
    monkeypatch.setattr(idk.sdk_opts, "image_thumbnail_format", "WEBP")
    img = idk.thumbnail(jpg_file)
    img = idk.image_strip_metadata(img)
    durl = idk.image_to_data_url(img)
    assert (
        durl
        == "data:image/webp;base64,UklGRsoFAABXRUJQVlA4IL4FAADwIQCdASqAAFUAPxF2sFKsJyQnrVjKkYAiCWdq5lv09vPSNmmbj7iZk4N2TVzS3f28KvARwIDCCFvYB08Zj/OGDuXd6KbVZ1elL5+Thy+MASDkNoK3zhL9GbtOVulvlPZi02n55mWY9CqrpVB2wKfvipBFcBcC4Sg/5PoOp3eoPKOGSJH9HC5mdxEVBgI3Xb4UZBcKL4vaPglyyNsiyi2oQL6V8mqn4B45E4s7LciIC8MzbBI0PZPpw8pGu6fDYdxfBVryj3U7OLzuFgWbs0fyKFGyMlUFwI0LpOM3ZWQwQzvHD51lUxY/LTrpg4KugjrBaGL9iZQ31+p4BMvrPtIBTfdfqtJjlR3HdBxz5kR2DLWg+3sVrYIAAP73G07RB5tivGcYPEKMrM9JwYUPlKYGNDGfaHbgcX/2Pskovgagq4KXbe9za0j8khE+6veHlb0RAbLm6BCJNwz/vveUdZlnuOzoVmWWfOZd8Ie8y1XXzwi86aoQ04eUKBPxKdP9F0d1UVZRF/IgMtdRAWJyoesBmm8PP0E1f5LBVPvTdD2sgmUpyp+71BDzGxIVwCyYFaAWL0qbna5qyWKa6IBXSiD3JA4aOBOaJTN6/dJ4ipXCu1Vorx8oq1gfhZZoYMeRT5V+dNiseCFF8tKV4sywXdAQmQ8kDczrpLG4r7M1D1nMPFerm9eaJVUIPr8nW4kYYcuByz4W1xbH6AXgkoCdWeDyu+bx25+3/uFp3Iaj+WtU2WRZBwo0BcwOb2LrKeppY8pX8m75I+DWB+rVkr9vFpqddnR/y/pQSoQVtQ/V+ay0u3Pm+zH9otaUo9c9hLA9Ovh2O39BRB4Y1TzJl9/7AFanErXAGacEZ8FL609EWBBG80R93ngrpuodAAOM3tKd1Rx95Tzh33LJ9YyxVZPzCwEQoqvWrEo7PDmTVTPk3dMJRrkMtZKO51agOkic1/PCjlwYpHi7W46pEIe9zBvTBDaZmtWlG6rjNYGmjH0tuDM/5cpfUXCACEBsfHQ87HxUDbXCUmtp5dyq7CyzkReQ3TZ2PRmdd54AF2SDnb0j+gThNhKymJWBjhbjBgeiKC+OZArkHP5pB/mEezzI1WjlBXEPrcY2BZItNI2RpJNSLUQl1N1YeiG0Q3aOvXkIBOh9ABUOlwpyT6+dSxz9+nxN3SfVRNTp98VfJ7qnPuFABXSPkNQIo2ki6QvVKUpBxFf3l1TducABMqiWzynRl6Ezrq7uJMVhUO8kEww6oGjGgxYPsXKUb53DHE2+ZxEUMKhq09qW2N7G8lsdpYSjLDCJ1oYVzqopUBD9coQMEeWvtD/cYK4Ktb54gkKJa/t+2ItBXw6wFdoL38sverCYjBbYTh6hqL1RD9Op++Kphe77COHhZmxqk8o56QOeJLUnVQxN+NzJ81LbU/sw+1t5lfwlXZ5xOdjRV5Qv12UY2jMjlRNhpeO7AdIx3KKz2l1r+R2pfFk3OdY2Gp+/kmGncrOopGVZjCrldoW+6Y8tShnhKZN8+U43VZv2NdPIPcmEyHPtqE20dC0ZGpdNLdMXAySTLlHbCg07FmxbkBDJRxQLdLiY5wLBmLYplJjZTM8eVYqjQnkPts5chrj9SCizfwTC2TWqkCsUVrI/k2aQi8QcXfaulPqKLDy86JJYmk+bKOnio/z+cxXq3PvzISKGJFji8mtMoaZTi3Np0M5c2DE0a6XT3CKifk8J/uDHDicJmW3wRjvpynimvfeG527ysulnf/R4HtIbFeM4HrGNeI1PO8gJOc+W/lC0xgNDDABv6p9fVq0sXthbhuM9OXq/zdDf6e+TRtB5rFsCW1jUDq4+iiuzx1dSY7wOs9K7PiflWrD8HQamEqVUSlE3KCTuWoDbdtrX9fRdmj+IDIHoxU3Eppp+QWTuxIjyrtX9jAJ291BqVHal2uIWHrq+0eOdK6VkY3O8kJXEmExFcSYmqiJZwAA="
    )


def test_thumbnail_data_url_avif(jpg_file, monkeypatch):
    monkeypatch.setattr(idk.sdk_opts, "image_thumbnail_format", "AVIF")
    img = idk.thumbnail(jpg_file)
    img = idk.image_strip_metadata(img)
    durl = idk.image_to_data_url(img)
    assert (
        durl
        == "data:image/avif;base64,AAAAIGZ0eXBhdmlmAAAAAGF2aWZtaWYxbWlhZk1BMUIAAADrbWV0YQAAAAAAAAAhaGRscgAAAAAAAAAAcGljdAAAAAAAAAAAAAAAAAAAAAAOcGl0bQAAAAAAAQAAAB5pbG9jAAAAAEQAAAEAAQAAAAEAAAETAAAD4wAAAChpaW5mAAAAAAABAAAAGmluZmUCAAAAAAEAAGF2MDFDb2xvcgAAAABqaXBycAAAAEtpcGNvAAAAFGlzcGUAAAAAAAAAgAAAAFUAAAAQcGl4aQAAAAADCAgIAAAADGF2MUOBAAwAAAAAE2NvbHJuY2x4AAEADQAGgAAAABdpcG1hAAAAAAAAAAEAAQQBAoMEAAAD621kYXQSAAoJGBm/1GCAhoNCMtMHEsAGmmmhQNgPaOHK3Lj4IJC+2rSLcjjQ6qSa4Sh3PN7wDJQdnP4z0vquxHHludIpO/Cxi6W710N0mwqxqZyvKF1OmdyNOlWi97YF9s1FFaoHfPGogO2U0PmaCY8zZn813I4m+hPJI1bHzhcHXPlcZtkt7506ED1O2LfjfLMpcda/S1LYthDkK0UmrgLuVz/GAzxVXee6U8FS3QCvmVTSi4Vm9z0XQQbqlv50v4dO0RC5Sx0k+T+SHvQU07sTfUE07F63X02KkA8Kd2QWsQkE8Dt6wqoLIUPNCD+z0RPVQ40UXX/HkvYMdR+p8lZOXOvgtDDvA7yPVctWLp1a3DMBTUKyxRUQaqNxdkmonaYJqQnmGi+C1EP0PNuAj8evWbtQlQHyPq8Ek5kTcrqowGvx/1vvzDxGvf+uM/wMiVTwXjaQQv+uwS69N8P+Fpkov5VjHYVWSyDIPvfFnBl3XIKPr6nOeCjJRE2AirGhxSqvIHAYuPPPQVGRxmpjlNq/Z0saQn7iP6FO3sz1Xd6Q8DXHzlVJeNEP4pmy524Lae1xvZnaFbBBKyQYFzfsLMcxWzMGKNYHY+vyfv0obGaIUXMrQlEpATCdhlpF9DQxqWNj0zWukqaCa7saKZGdJYpZNYcv0kM8t+RIRM7opVRPmbKbldfGDWgomWzUieJMFUDSmoqUNK260lzgFrIJphzcojNPEz12eQpuOE3fxcFuvnEINfqSDCQcNWle1gqeH2AWO/cGhPIxk09MBsm8b4388LECpiIgbPOZDHZapM/I70wVvXgD8i5N5y7ZjsEZnvoD5OCCQVHQBfUqCseK5tW7RgdwMI/3fYbUo4zsF2612dUG/um5VkjaeQljvI5j7MNo5E+7le9qWBxJ46T88PVcL4UKLo0/dJZR0LFZg4LIlJNLVxRr2YFcQ/DfSL7Pu1JkhNZl2vzCzQzGwVTbdaQA6F2GCXfo0s2TtVZhv6sZmrxKOeCWMcu813YchoCWrnqcvCtgnhH7WTNuKEsU7x3/Ueo6BDUk5EYkAqKXL7b898pgDYj9jss7PqvnIC99sDMB5B2GfcOdIC6I/E/wzfaarUftFdlRK9C+c2DxsxlG7GsLwZ8IItkJ6nPdhdZeFg02xT81hQX0Q23IvCNdXnFbZkoWyPZ9O/VnuN2CezFmISCgQg4e6NVWQfWDoPRf0eYGfPVp/yICJzMviFvnMQmfw5MX8ZyrmFVB6yHmq0lCTjRPuII27xMrtGP/NK1v9iac5xQqwFvgIMbSxjYG6ULWWyI4BvABd6W5HSnsm/Zj/ly13N1MQA=="
    )
