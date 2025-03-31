import iscc_sdk as idk


def test_code_iscc_text(pdf_file):
    assert idk.code_iscc(pdf_file).dict(exclude={"generator"}) == {
        "@type": "TextDigitalDocument",
        "characters": 16995,
        "datahash": "1e207ad5c7dbf6a6538f15fd0439e0dc5ba03a043ea23f072aa4e2ba830811bdb5f0",
        "filename": "text.pdf",
        "filesize": 188280,
        "iscc": "ISCC:KACV5NAQXBCHCWFWMNALVJHBLB7X7IFU4H2JIVUSWF5NLR6362TFHDY",
        "mediatype": "application/pdf",
        "metahash": "1e201da548c5285ed35f293c3e22c2f050e037643aae8cf9244b532a162ff5031f52",
        "mode": "text",
        "name": "title from metadata",
        "thumbnail": "data:image/webp;base64,UklGRrICAABXRUJQVlA4IKYCAACwEACdASpjAIAAPxF+t1WsJ6UjJ3O6yYAiCWk+1vbxe/5u5aUMiMOGBEPHRva7LyiDyJ+apJUAnOLZT8AuhIuIwlOEx2gv1bbGtIyCMNkXjmnAppQQ6vUNHQnJGJAbAA0SzARfH+PI65QQXALNcIXxtbwhDki9YIFU4C3AYpy+NQ4HW+ixxOaE9S1jKMZYAP7xbhpUUUzl4ZYGOS+0BwqydCAnxPlMIn1kN0WBQI3eoPNfsrVdOYciWd83NW3PtkJaLZ6N5NqjX1YCAV3WH/JowbLN2psSAkdytfqt0AbMTIFFchPapmB5WQ7eUQmicce07fManIeUEfadOLIxipAq9QxIUp3ztvoJWcfYlWTO+VIhFdZvnXGUEjbSbxW/dNfZ5iUbIP4uV+tEsfy7N0NQgev6d8kyPQAasfgksjMgDh18i/JeiPixrhAc+1A2LpDkDpnUe5Si7+ictdhg1xbyNGyfKW+zuNUwkZWr29FGkgxfz1O9L5p0Xa9dviDM6U6ikhi8jegP6Ff6yCOMT6ZSIiGICXBK9tCHqtxCJ+ma3Yszmy/Wm7peJvWHBiWqdEZKc/t+7pndgha9pQq2G4jhBtCs5DrtYR0jo94wvwjfeOnWf+wtt29cNo/uQqSGPoeZyiBBbaLtQ5R/EOtQgCYTGHa2h3rONLzLRlqyGzEcd3Sv05VpEAcYEqDlQuw0APpM2PUacoZk1+Mj05qHS4JBDiOL/+z0gT58T/+kJQs7O8gkOqhLisGHpJERYQdnkMcct8/Nqy2Cjvuc3zSbfK4cChsEY9jo0npzMAH4Ip3eBoIciC4JYPvHcmQvyM1XvI/MMq7sOOwoBsvkKApzjgB0RiMTLI5gPocAEN/XQf4U2rzUBkVx63Q6VgegIIzAANgMDgAAAAA=",
    }


def test_code_iscc_image(jpg_file):
    assert idk.code_iscc(jpg_file).dict(exclude={"generator"}) == {
        "@type": "ImageObject",
        "creator": "Some Cat Lover",
        "datahash": "1e2055529bfae5bdb3d530c52f44d13ccd6a7c710f63620dc2db1c43c5592ae2dc97",
        "filename": "img.jpg",
        "filesize": 35393,
        "height": 133,
        "iscc": "ISCC:KECWRY3VY6R5SNV4YNBTBHR4T2HGP3HKVFO7TYUP2BKVFG724W63HVI",
        "mediatype": "image/jpeg",
        "metahash": "1e209ce5052a03004657d8657167f53812718e9426d85b4cdd5106ef3d87412e6f64",
        "mode": "image",
        "name": "Concentrated Cat",
        "thumbnail": "data:image/webp;base64,UklGRsoFAABXRUJQVlA4IL4FAADwIQCdASqAAFUAPxF2sFKsJyQnrVjKkYAiCWdq5lv09vPSNmmbj7iZk4N2TVzS3f28KvARwIDCCFvYB08Zj/OGDuXd6KbVZ1elL5+Thy+MASDkNoK3zhL9GbtOVulvlPZi02n55mWY9CqrpVB2wKfvipBFcBcC4Sg/5PoOp3eoPKOGSJH9HC5mdxEVBgI3Xb4UZBcKL4vaPglyyNsiyi2oQL6V8mqn4B45E4s7LciIC8MzbBI0PZPpw8pGu6fDYdxfBVryj3U7OLzuFgWbs0fyKFGyMlUFwI0LpOM3ZWQwQzvHD51lUxY/LTrpg4KugjrBaGL9iZQ31+p4BMvrPtIBTfdfqtJjlR3HdBxz5kR2DLWg+3sVrYIAAP73G07RB5tivGcYPEKMrM9JwYUPlKYGNDGfaHbgcX/2Pskovgagq4KXbe9za0j8khE+6veHlb0RAbLm6BCJNwz/vveUdZlnuOzoVmWWfOZd8Ie8y1XXzwi86aoQ04eUKBPxKdP9F0d1UVZRF/IgMtdRAWJyoesBmm8PP0E1f5LBVPvTdD2sgmUpyp+71BDzGxIVwCyYFaAWL0qbna5qyWKa6IBXSiD3JA4aOBOaJTN6/dJ4ipXCu1Vorx8oq1gfhZZoYMeRT5V+dNiseCFF8tKV4sywXdAQmQ8kDczrpLG4r7M1D1nMPFerm9eaJVUIPr8nW4kYYcuByz4W1xbH6AXgkoCdWeDyu+bx25+3/uFp3Iaj+WtU2WRZBwo0BcwOb2LrKeppY8pX8m75I+DWB+rVkr9vFpqddnR/y/pQSoQVtQ/V+ay0u3Pm+zH9otaUo9c9hLA9Ovh2O39BRB4Y1TzJl9/7AFanErXAGacEZ8FL609EWBBG80R93ngrpuodAAOM3tKd1Rx95Tzh33LJ9YyxVZPzCwEQoqvWrEo7PDmTVTPk3dMJRrkMtZKO51agOkic1/PCjlwYpHi7W46pEIe9zBvTBDaZmtWlG6rjNYGmjH0tuDM/5cpfUXCACEBsfHQ87HxUDbXCUmtp5dyq7CyzkReQ3TZ2PRmdd54AF2SDnb0j+gThNhKymJWBjhbjBgeiKC+OZArkHP5pB/mEezzI1WjlBXEPrcY2BZItNI2RpJNSLUQl1N1YeiG0Q3aOvXkIBOh9ABUOlwpyT6+dSxz9+nxN3SfVRNTp98VfJ7qnPuFABXSPkNQIo2ki6QvVKUpBxFf3l1TducABMqiWzynRl6Ezrq7uJMVhUO8kEww6oGjGgxYPsXKUb53DHE2+ZxEUMKhq09qW2N7G8lsdpYSjLDCJ1oYVzqopUBD9coQMEeWvtD/cYK4Ktb54gkKJa/t+2ItBXw6wFdoL38sverCYjBbYTh6hqL1RD9Op++Kphe77COHhZmxqk8o56QOeJLUnVQxN+NzJ81LbU/sw+1t5lfwlXZ5xOdjRV5Qv12UY2jMjlRNhpeO7AdIx3KKz2l1r+R2pfFk3OdY2Gp+/kmGncrOopGVZjCrldoW+6Y8tShnhKZN8+U43VZv2NdPIPcmEyHPtqE20dC0ZGpdNLdMXAySTLlHbCg07FmxbkBDJRxQLdLiY5wLBmLYplJjZTM8eVYqjQnkPts5chrj9SCizfwTC2TWqkCsUVrI/k2aQi8QcXfaulPqKLDy86JJYmk+bKOnio/z+cxXq3PvzISKGJFji8mtMoaZTi3Np0M5c2DE0a6XT3CKifk8J/uDHDicJmW3wRjvpynimvfeG527ysulnf/R4HtIbFeM4HrGNeI1PO8gJOc+W/lC0xgNDDABv6p9fVq0sXthbhuM9OXq/zdDf6e+TRtB5rFsCW1jUDq4+iiuzx1dSY7wOs9K7PiflWrD8HQamEqVUSlE3KCTuWoDbdtrX9fRdmj+IDIHoxU3Eppp+QWTuxIjyrtX9jAJ291BqVHal2uIWHrq+0eOdK6VkY3O8kJXEmExFcSYmqiJZwAA=",
        "width": 200,
    }


def test_code_iscc_audio(mp3_file):
    assert idk.code_iscc(mp3_file).dict(exclude={"generator"}) == {
        "@type": "AudioObject",
        "iscc": "ISCC:KIC2JKSX7OH5PBIENISKEJTS4TRKHYJBCZDNLQXYILWJHQAP3N3KPTQ",
        "name": "Belly Button",
        "datahash": "1e20ec93c00fdb76a7cec587e4a2bddfa8d0a0bac8110d0c7130c351ea07c366d626",
        "duration": 15.543,
        "filesize": 225707,
        "filename": "audio.mp3",
        "mediatype": "audio/mpeg",
        "metahash": "1e20c4933dc8c03ea58568159a1cbfb04132c7db93b6b4cd025ffd4db37f52a4756f",
        "mode": "audio",
    }


def test_code_iscc_video(mp4_file):
    assert idk.code_iscc(mp4_file).dict(exclude={"generator"}) == {
        "@type": "VideoObject",
        "datahash": "1e209d412d76d9d516d07bb60f1ab3c1a5c1b176ed4f1cec94c96222a5d013ec3e38",
        "duration": 60.14,
        "filename": "video.mp4",
        "filesize": 2161914,
        "fps": 24.0,
        "height": 144,
        "iscc": "ISCC:KMCV6UK6BSXJ3I4GLYHIH5A5DNZPYBWQO33FNHPQFOOUCLLW3HKRNUA",
        "language": "en",
        "mediatype": "video/mp4",
        "metahash": "1e2096c0a53475a186ce37622aba7ba70651fc62cc8150f59eee6d17dc16d9bfbf25",
        "mode": "video",
        "name": "Kali by Anokato - Spiral Sessions 2019",
        "thumbnail": "data:image/webp;base64,UklGRtoDAABXRUJQVlA4IM4DAADwEgCdASqAAGkAPxGCtVUsKL+jJds7o/AiCUAZxC/zSVryP9F5Wd4MpYyh31Oop3Y1gW+FUMLF+LH50r/j5ektgrr1PhBZy2lHUxe8+j3fLIkk3vEgo4XeUcOHki+nHkQKHGj5abzYzMffF3kH7eD7WVSlP9sdBVmH36ki52xuj8Tk7TEMq1cJgUI72s4iUWvXE39Rx9IcYSWg4avx6FxgAP7zJTKAANvYY6Iw1uv7ee7/vvndS/7h+OCS0L1oJhmJLVuUfE0V9cJlj4uTf3yAlsbKN2mzv7sCNYAVC8Ttl/gV6o1g6EcCV1l7gSkInYzwpJ4ABnOFk6RcmbZF3DUwOtdwsDkuBgt3QIWsiGX0ZTNwmI7TUHrdLCUzJrLwt0FNQKEwY1KRt4C3BwSIFBVQvjLGpPyVk9pjvlkqOq7PqLbsffEJgg56cKlVkm8Zql5Gg+0kH99bXXXR35537NfxxOeWnf+82PPohNE4LngSygQEgXRyQ4E4GI94UZpn1N56npj/kI+XE5NOyP5gOHpxrYu/KoVT7tMJHvP4rOUku85WEhNrm7iyxPsk5dOMVKEd0QntCmXLob62Qxq635euCrZC9g5wrD0y/W9xCF4rqkNvPgdZn85cXFuolbCqIidgX2GS6HBzTRNQ9yhQ88o/IwEfc34bpx+c/onylwkEsEvqqLmUVO0sN7+nMHlZWhxwaV4rWervpFRDvbsXJz/o1XFFqkraQ5MPrD12P8mDsjDPiKlXExY7aa1NDNLfsZi/XbaBf9Ju0W2n0JVJGwJuoFzAhReTE4jHzbpeCo3/ZvC7/ISLeiPoN8F0KAXTLIy31YaAvPlB8+AYsSEvcMZJQL/7mxoCBetvf/eEcMPPpfWzabWJfCwXEtjVQBmahu2qlJZD5MdXAlA0NgNbeJwZYBtHM29vKBHHoVBE/liCWVaDmgFUdEk+jF6pPFPH5eVd22zxDEIqzRpN0Xzl/5HI656sCzWOb9T1uQN5kw21KOci1ulRYNBplfqlQFoUEiuSE26ub7ezJUM4R7dEzIW9RbM4Yweacq54M+nLnfhaD/R9yjqtIzvpZz8PFjVwPKbZzHX3PmraHLrKET/2IzadluRfJRSUnMInZpWTAUgyAoV7h1ULtK1PcivZKBoCz54G9XrroBgsNKn6N/QLdJWvwzC/RrSSTmXTw5gCJT7wD+ZxcwUAFrA7U+j1icfQj2w+pUIPHv+bmki4y7GxH6Y2HzeRVTnSQQS5JP2uwM8blPWX3WH5lqhngyLP46HTbAQH7o7KUzF6v8cyp+gAAA==",
        "width": 176,
    }


def test_code_meta_image(jpg_file):
    assert idk.code_meta(jpg_file).dict() == {
        "iscc": "ISCC:AAAWRY3VY6R5SNV4",
        "name": "Concentrated Cat",
        "creator": "Some Cat Lover",
        "width": 200,
        "height": 133,
        "metahash": "1e209ce5052a03004657d8657167f53812718e9426d85b4cdd5106ef3d87412e6f64",
    }


def test_code_meta_audio(mp3_file):
    assert idk.code_meta(mp3_file).dict() == {
        "duration": 15.543,
        "iscc": "ISCC:AAA2JKSX7OH5PBIE",
        "metahash": "1e20c4933dc8c03ea58568159a1cbfb04132c7db93b6b4cd025ffd4db37f52a4756f",
        "name": "Belly Button",
    }


def test_code_meta_video(mp4_file):
    assert idk.code_meta(mp4_file).dict() == {
        "duration": 60.14,
        "fps": 24.0,
        "height": 144,
        "iscc": "ISCC:AAAV6UK6BSXJ3I4G",
        "language": "en",
        "metahash": "1e2096c0a53475a186ce37622aba7ba70651fc62cc8150f59eee6d17dc16d9bfbf25",
        "name": "Kali by Anokato - Spiral Sessions 2019",
        "width": 176,
    }


def test_code_meta_image_no_meta(bmp_file):
    assert idk.code_meta(bmp_file).dict() == {
        "iscc": "ISCC:AAA374FA7VF3FWZQ",
        "name": "img",
        "width": 200,
        "height": 133,
        "metahash": "1e20bff0a0fd4bb2db301741c4c9cbfced1085e2051e6009edb12b004330fa7f5111",
    }


def test_code_content(jpg_file):
    assert idk.code_content(jpg_file).dict() == {
        "@type": "ImageObject",
        "creator": "Some Cat Lover",
        "height": 133,
        "iscc": "ISCC:EEA4GQZQTY6J5DTH",
        "mediatype": "image/jpeg",
        "mode": "image",
        "name": "Concentrated Cat",
        "thumbnail": "data:image/webp;base64,UklGRsoFAABXRUJQVlA4IL4FAADwIQCdASqAAFUAPxF2sFKsJyQnrVjKkYAiCWdq5lv09vPSNmmbj7iZk4N2TVzS3f28KvARwIDCCFvYB08Zj/OGDuXd6KbVZ1elL5+Thy+MASDkNoK3zhL9GbtOVulvlPZi02n55mWY9CqrpVB2wKfvipBFcBcC4Sg/5PoOp3eoPKOGSJH9HC5mdxEVBgI3Xb4UZBcKL4vaPglyyNsiyi2oQL6V8mqn4B45E4s7LciIC8MzbBI0PZPpw8pGu6fDYdxfBVryj3U7OLzuFgWbs0fyKFGyMlUFwI0LpOM3ZWQwQzvHD51lUxY/LTrpg4KugjrBaGL9iZQ31+p4BMvrPtIBTfdfqtJjlR3HdBxz5kR2DLWg+3sVrYIAAP73G07RB5tivGcYPEKMrM9JwYUPlKYGNDGfaHbgcX/2Pskovgagq4KXbe9za0j8khE+6veHlb0RAbLm6BCJNwz/vveUdZlnuOzoVmWWfOZd8Ie8y1XXzwi86aoQ04eUKBPxKdP9F0d1UVZRF/IgMtdRAWJyoesBmm8PP0E1f5LBVPvTdD2sgmUpyp+71BDzGxIVwCyYFaAWL0qbna5qyWKa6IBXSiD3JA4aOBOaJTN6/dJ4ipXCu1Vorx8oq1gfhZZoYMeRT5V+dNiseCFF8tKV4sywXdAQmQ8kDczrpLG4r7M1D1nMPFerm9eaJVUIPr8nW4kYYcuByz4W1xbH6AXgkoCdWeDyu+bx25+3/uFp3Iaj+WtU2WRZBwo0BcwOb2LrKeppY8pX8m75I+DWB+rVkr9vFpqddnR/y/pQSoQVtQ/V+ay0u3Pm+zH9otaUo9c9hLA9Ovh2O39BRB4Y1TzJl9/7AFanErXAGacEZ8FL609EWBBG80R93ngrpuodAAOM3tKd1Rx95Tzh33LJ9YyxVZPzCwEQoqvWrEo7PDmTVTPk3dMJRrkMtZKO51agOkic1/PCjlwYpHi7W46pEIe9zBvTBDaZmtWlG6rjNYGmjH0tuDM/5cpfUXCACEBsfHQ87HxUDbXCUmtp5dyq7CyzkReQ3TZ2PRmdd54AF2SDnb0j+gThNhKymJWBjhbjBgeiKC+OZArkHP5pB/mEezzI1WjlBXEPrcY2BZItNI2RpJNSLUQl1N1YeiG0Q3aOvXkIBOh9ABUOlwpyT6+dSxz9+nxN3SfVRNTp98VfJ7qnPuFABXSPkNQIo2ki6QvVKUpBxFf3l1TducABMqiWzynRl6Ezrq7uJMVhUO8kEww6oGjGgxYPsXKUb53DHE2+ZxEUMKhq09qW2N7G8lsdpYSjLDCJ1oYVzqopUBD9coQMEeWvtD/cYK4Ktb54gkKJa/t+2ItBXw6wFdoL38sverCYjBbYTh6hqL1RD9Op++Kphe77COHhZmxqk8o56QOeJLUnVQxN+NzJ81LbU/sw+1t5lfwlXZ5xOdjRV5Qv12UY2jMjlRNhpeO7AdIx3KKz2l1r+R2pfFk3OdY2Gp+/kmGncrOopGVZjCrldoW+6Y8tShnhKZN8+U43VZv2NdPIPcmEyHPtqE20dC0ZGpdNLdMXAySTLlHbCg07FmxbkBDJRxQLdLiY5wLBmLYplJjZTM8eVYqjQnkPts5chrj9SCizfwTC2TWqkCsUVrI/k2aQi8QcXfaulPqKLDy86JJYmk+bKOnio/z+cxXq3PvzISKGJFji8mtMoaZTi3Np0M5c2DE0a6XT3CKifk8J/uDHDicJmW3wRjvpynimvfeG527ysulnf/R4HtIbFeM4HrGNeI1PO8gJOc+W/lC0xgNDDABv6p9fVq0sXthbhuM9OXq/zdDf6e+TRtB5rFsCW1jUDq4+iiuzx1dSY7wOs9K7PiflWrD8HQamEqVUSlE3KCTuWoDbdtrX9fRdmj+IDIHoxU3Eppp+QWTuxIjyrtX9jAJ291BqVHal2uIWHrq+0eOdK6VkY3O8kJXEmExFcSYmqiJZwAA=",
        "width": 200,
    }


def test_code_text(docx_file):
    assert idk.code_text(docx_file).dict() == {
        "iscc": "ISCC:EAAQMBEYQF6457DP",
        "name": "title from metadata",
        "creator": "titusz",
        "characters": 4951,
    }


def test_code_text_granular(docx_file, monkeypatch):
    monkeypatch.setattr(idk.sdk_opts, "granular", True)
    assert idk.code_text(docx_file).dict() == {
        "characters": 4951,
        "creator": "titusz",
        "features": [
            {
                "maintype": "content",
                "offsets": [0, 997, 1454, 2123, 4942, 5399, 6068],
                "simprints": [
                    "k5TpwXVE3j9N5IBxm36c4hkXP6fHOv8bkY2f68_8XSg",
                    "OERRAF2u5WWuLHZLZzgcCSoCoL9R0NYrBJD7s7A43t0",
                    "AARYEMzu5WEOfTZq5ixNLcoThJ5AgJYNRICysqEs3v0",
                    "lp6NgXnE_C1c6ij12-w04RwZN4XJyP0KgIrbKYX81yo",
                    "OERRAF2u5WWuLHZLZzgcCSoCoL9R0NYrBJD7s7A43t0",
                    "AARYEMzu5WEOfTZq5ixNLcoThJ5AgJYNRICysqEs3v0",
                    "JfC6tnH1BuHFMviS2deReiUuelIIMvWWOozU6afjErU",
                ],
                "sizes": [997, 457, 669, 2819, 457, 669, 1],
                "subtype": "text",
                "version": 0,
            }
        ],
        "iscc": "ISCC:EAAQMBEYQF6457DP",
        "name": "title from metadata",
    }


def test_code_image(jpg_file):
    assert idk.code_image(jpg_file).dict() == {
        "creator": "Some Cat Lover",
        "height": 133,
        "iscc": "ISCC:EEA4GQZQTY6J5DTH",
        "name": "Concentrated Cat",
        "thumbnail": "data:image/webp;base64,UklGRsoFAABXRUJQVlA4IL4FAADwIQCdASqAAFUAPxF2sFKsJyQnrVjKkYAiCWdq5lv09vPSNmmbj7iZk4N2TVzS3f28KvARwIDCCFvYB08Zj/OGDuXd6KbVZ1elL5+Thy+MASDkNoK3zhL9GbtOVulvlPZi02n55mWY9CqrpVB2wKfvipBFcBcC4Sg/5PoOp3eoPKOGSJH9HC5mdxEVBgI3Xb4UZBcKL4vaPglyyNsiyi2oQL6V8mqn4B45E4s7LciIC8MzbBI0PZPpw8pGu6fDYdxfBVryj3U7OLzuFgWbs0fyKFGyMlUFwI0LpOM3ZWQwQzvHD51lUxY/LTrpg4KugjrBaGL9iZQ31+p4BMvrPtIBTfdfqtJjlR3HdBxz5kR2DLWg+3sVrYIAAP73G07RB5tivGcYPEKMrM9JwYUPlKYGNDGfaHbgcX/2Pskovgagq4KXbe9za0j8khE+6veHlb0RAbLm6BCJNwz/vveUdZlnuOzoVmWWfOZd8Ie8y1XXzwi86aoQ04eUKBPxKdP9F0d1UVZRF/IgMtdRAWJyoesBmm8PP0E1f5LBVPvTdD2sgmUpyp+71BDzGxIVwCyYFaAWL0qbna5qyWKa6IBXSiD3JA4aOBOaJTN6/dJ4ipXCu1Vorx8oq1gfhZZoYMeRT5V+dNiseCFF8tKV4sywXdAQmQ8kDczrpLG4r7M1D1nMPFerm9eaJVUIPr8nW4kYYcuByz4W1xbH6AXgkoCdWeDyu+bx25+3/uFp3Iaj+WtU2WRZBwo0BcwOb2LrKeppY8pX8m75I+DWB+rVkr9vFpqddnR/y/pQSoQVtQ/V+ay0u3Pm+zH9otaUo9c9hLA9Ovh2O39BRB4Y1TzJl9/7AFanErXAGacEZ8FL609EWBBG80R93ngrpuodAAOM3tKd1Rx95Tzh33LJ9YyxVZPzCwEQoqvWrEo7PDmTVTPk3dMJRrkMtZKO51agOkic1/PCjlwYpHi7W46pEIe9zBvTBDaZmtWlG6rjNYGmjH0tuDM/5cpfUXCACEBsfHQ87HxUDbXCUmtp5dyq7CyzkReQ3TZ2PRmdd54AF2SDnb0j+gThNhKymJWBjhbjBgeiKC+OZArkHP5pB/mEezzI1WjlBXEPrcY2BZItNI2RpJNSLUQl1N1YeiG0Q3aOvXkIBOh9ABUOlwpyT6+dSxz9+nxN3SfVRNTp98VfJ7qnPuFABXSPkNQIo2ki6QvVKUpBxFf3l1TducABMqiWzynRl6Ezrq7uJMVhUO8kEww6oGjGgxYPsXKUb53DHE2+ZxEUMKhq09qW2N7G8lsdpYSjLDCJ1oYVzqopUBD9coQMEeWvtD/cYK4Ktb54gkKJa/t+2ItBXw6wFdoL38sverCYjBbYTh6hqL1RD9Op++Kphe77COHhZmxqk8o56QOeJLUnVQxN+NzJ81LbU/sw+1t5lfwlXZ5xOdjRV5Qv12UY2jMjlRNhpeO7AdIx3KKz2l1r+R2pfFk3OdY2Gp+/kmGncrOopGVZjCrldoW+6Y8tShnhKZN8+U43VZv2NdPIPcmEyHPtqE20dC0ZGpdNLdMXAySTLlHbCg07FmxbkBDJRxQLdLiY5wLBmLYplJjZTM8eVYqjQnkPts5chrj9SCizfwTC2TWqkCsUVrI/k2aQi8QcXfaulPqKLDy86JJYmk+bKOnio/z+cxXq3PvzISKGJFji8mtMoaZTi3Np0M5c2DE0a6XT3CKifk8J/uDHDicJmW3wRjvpynimvfeG527ysulnf/R4HtIbFeM4HrGNeI1PO8gJOc+W/lC0xgNDDABv6p9fVq0sXthbhuM9OXq/zdDf6e+TRtB5rFsCW1jUDq4+iiuzx1dSY7wOs9K7PiflWrD8HQamEqVUSlE3KCTuWoDbdtrX9fRdmj+IDIHoxU3Eppp+QWTuxIjyrtX9jAJ291BqVHal2uIWHrq+0eOdK6VkY3O8kJXEmExFcSYmqiJZwAA=",
        "width": 200,
    }


def test_code_video(mp4_file):
    assert idk.code_video(mp4_file).dict() == {
        "duration": 60.14,
        "fps": 24.0,
        "height": 144,
        "iscc": "ISCC:EMAV4DUD6QORW4X4",
        "language": "en",
        "name": "Kali by Anokato - Spiral Sessions 2019",
        "thumbnail": "data:image/webp;base64,UklGRtoDAABXRUJQVlA4IM4DAADwEgCdASqAAGkAPxGCtVUsKL+jJds7o/AiCUAZxC/zSVryP9F5Wd4MpYyh31Oop3Y1gW+FUMLF+LH50r/j5ektgrr1PhBZy2lHUxe8+j3fLIkk3vEgo4XeUcOHki+nHkQKHGj5abzYzMffF3kH7eD7WVSlP9sdBVmH36ki52xuj8Tk7TEMq1cJgUI72s4iUWvXE39Rx9IcYSWg4avx6FxgAP7zJTKAANvYY6Iw1uv7ee7/vvndS/7h+OCS0L1oJhmJLVuUfE0V9cJlj4uTf3yAlsbKN2mzv7sCNYAVC8Ttl/gV6o1g6EcCV1l7gSkInYzwpJ4ABnOFk6RcmbZF3DUwOtdwsDkuBgt3QIWsiGX0ZTNwmI7TUHrdLCUzJrLwt0FNQKEwY1KRt4C3BwSIFBVQvjLGpPyVk9pjvlkqOq7PqLbsffEJgg56cKlVkm8Zql5Gg+0kH99bXXXR35537NfxxOeWnf+82PPohNE4LngSygQEgXRyQ4E4GI94UZpn1N56npj/kI+XE5NOyP5gOHpxrYu/KoVT7tMJHvP4rOUku85WEhNrm7iyxPsk5dOMVKEd0QntCmXLob62Qxq635euCrZC9g5wrD0y/W9xCF4rqkNvPgdZn85cXFuolbCqIidgX2GS6HBzTRNQ9yhQ88o/IwEfc34bpx+c/onylwkEsEvqqLmUVO0sN7+nMHlZWhxwaV4rWervpFRDvbsXJz/o1XFFqkraQ5MPrD12P8mDsjDPiKlXExY7aa1NDNLfsZi/XbaBf9Ju0W2n0JVJGwJuoFzAhReTE4jHzbpeCo3/ZvC7/ISLeiPoN8F0KAXTLIy31YaAvPlB8+AYsSEvcMZJQL/7mxoCBetvf/eEcMPPpfWzabWJfCwXEtjVQBmahu2qlJZD5MdXAlA0NgNbeJwZYBtHM29vKBHHoVBE/liCWVaDmgFUdEk+jF6pPFPH5eVd22zxDEIqzRpN0Xzl/5HI656sCzWOb9T1uQN5kw21KOci1ulRYNBplfqlQFoUEiuSE26ub7ezJUM4R7dEzIW9RbM4Yweacq54M+nLnfhaD/R9yjqtIzvpZz8PFjVwPKbZzHX3PmraHLrKET/2IzadluRfJRSUnMInZpWTAUgyAoV7h1ULtK1PcivZKBoCz54G9XrroBgsNKn6N/QLdJWvwzC/RrSSTmXTw5gCJT7wD+ZxcwUAFrA7U+j1icfQj2w+pUIPHv+bmki4y7GxH6Y2HzeRVTnSQQS5JP2uwM8blPWX3WH5lqhngyLP46HTbAQH7o7KUzF6v8cyp+gAAA==",
        "width": 176,
    }


def test_code_data(png_file):
    assert idk.code_data(png_file) == {"iscc": "ISCC:GAAXUI3LCN7D7VDE"}


def test_code_instance(png_file):
    assert idk.code_instance(png_file).dict() == {
        "datahash": "1e20feb85f1709f51ebf31c2feab2092a61826da36cc79eddc4cb04800b47db146a6",
        "filesize": 54595,
        "iscc": "ISCC:IAA75OC7C4E7KHV7",
    }


def test_code_iscc_non_uri_metadata(jpg_file):
    new_file = idk.image_meta_embed(jpg_file, idk.IsccMeta.construct(license="Hello World"))
    assert idk.code_iscc(new_file).dict(exclude={"generator"}) == {
        "@type": "ImageObject",
        "creator": "Some Cat Lover",
        "datahash": "1e2010f846e2a950469a4b0e310accd76574e019faa858805ba4f6543498623e53ed",
        "filename": "img.jpg",
        "filesize": 35426,
        "height": 133,
        "iscc": "ISCC:KECWRY3VY6R5SNV4YNBTBHR4T2HGP3MLVE44D2E72AIPQRXCVFIENGQ",
        "license": "Hello World",
        "mediatype": "image/jpeg",
        "metahash": "1e209ce5052a03004657d8657167f53812718e9426d85b4cdd5106ef3d87412e6f64",
        "mode": "image",
        "name": "Concentrated Cat",
        "thumbnail": "data:image/webp;base64,UklGRsoFAABXRUJQVlA4IL4FAADwIQCdASqAAFUAPxF2sFKsJyQnrVjKkYAiCWdq5lv09vPSNmmbj7iZk4N2TVzS3f28KvARwIDCCFvYB08Zj/OGDuXd6KbVZ1elL5+Thy+MASDkNoK3zhL9GbtOVulvlPZi02n55mWY9CqrpVB2wKfvipBFcBcC4Sg/5PoOp3eoPKOGSJH9HC5mdxEVBgI3Xb4UZBcKL4vaPglyyNsiyi2oQL6V8mqn4B45E4s7LciIC8MzbBI0PZPpw8pGu6fDYdxfBVryj3U7OLzuFgWbs0fyKFGyMlUFwI0LpOM3ZWQwQzvHD51lUxY/LTrpg4KugjrBaGL9iZQ31+p4BMvrPtIBTfdfqtJjlR3HdBxz5kR2DLWg+3sVrYIAAP73G07RB5tivGcYPEKMrM9JwYUPlKYGNDGfaHbgcX/2Pskovgagq4KXbe9za0j8khE+6veHlb0RAbLm6BCJNwz/vveUdZlnuOzoVmWWfOZd8Ie8y1XXzwi86aoQ04eUKBPxKdP9F0d1UVZRF/IgMtdRAWJyoesBmm8PP0E1f5LBVPvTdD2sgmUpyp+71BDzGxIVwCyYFaAWL0qbna5qyWKa6IBXSiD3JA4aOBOaJTN6/dJ4ipXCu1Vorx8oq1gfhZZoYMeRT5V+dNiseCFF8tKV4sywXdAQmQ8kDczrpLG4r7M1D1nMPFerm9eaJVUIPr8nW4kYYcuByz4W1xbH6AXgkoCdWeDyu+bx25+3/uFp3Iaj+WtU2WRZBwo0BcwOb2LrKeppY8pX8m75I+DWB+rVkr9vFpqddnR/y/pQSoQVtQ/V+ay0u3Pm+zH9otaUo9c9hLA9Ovh2O39BRB4Y1TzJl9/7AFanErXAGacEZ8FL609EWBBG80R93ngrpuodAAOM3tKd1Rx95Tzh33LJ9YyxVZPzCwEQoqvWrEo7PDmTVTPk3dMJRrkMtZKO51agOkic1/PCjlwYpHi7W46pEIe9zBvTBDaZmtWlG6rjNYGmjH0tuDM/5cpfUXCACEBsfHQ87HxUDbXCUmtp5dyq7CyzkReQ3TZ2PRmdd54AF2SDnb0j+gThNhKymJWBjhbjBgeiKC+OZArkHP5pB/mEezzI1WjlBXEPrcY2BZItNI2RpJNSLUQl1N1YeiG0Q3aOvXkIBOh9ABUOlwpyT6+dSxz9+nxN3SfVRNTp98VfJ7qnPuFABXSPkNQIo2ki6QvVKUpBxFf3l1TducABMqiWzynRl6Ezrq7uJMVhUO8kEww6oGjGgxYPsXKUb53DHE2+ZxEUMKhq09qW2N7G8lsdpYSjLDCJ1oYVzqopUBD9coQMEeWvtD/cYK4Ktb54gkKJa/t+2ItBXw6wFdoL38sverCYjBbYTh6hqL1RD9Op++Kphe77COHhZmxqk8o56QOeJLUnVQxN+NzJ81LbU/sw+1t5lfwlXZ5xOdjRV5Qv12UY2jMjlRNhpeO7AdIx3KKz2l1r+R2pfFk3OdY2Gp+/kmGncrOopGVZjCrldoW+6Y8tShnhKZN8+U43VZv2NdPIPcmEyHPtqE20dC0ZGpdNLdMXAySTLlHbCg07FmxbkBDJRxQLdLiY5wLBmLYplJjZTM8eVYqjQnkPts5chrj9SCizfwTC2TWqkCsUVrI/k2aQi8QcXfaulPqKLDy86JJYmk+bKOnio/z+cxXq3PvzISKGJFji8mtMoaZTi3Np0M5c2DE0a6XT3CKifk8J/uDHDicJmW3wRjvpynimvfeG527ysulnf/R4HtIbFeM4HrGNeI1PO8gJOc+W/lC0xgNDDABv6p9fVq0sXthbhuM9OXq/zdDf6e+TRtB5rFsCW1jUDq4+iiuzx1dSY7wOs9K7PiflWrD8HQamEqVUSlE3KCTuWoDbdtrX9fRdmj+IDIHoxU3Eppp+QWTuxIjyrtX9jAJ291BqVHal2uIWHrq+0eOdK6VkY3O8kJXEmExFcSYmqiJZwAA=",
        "width": 200,
    }


def test_code_iscc_sum_fallback(svg_file, monkeypatch):
    monkeypatch.setattr(idk.sdk_opts, "fallback", True)
    result = idk.code_iscc(svg_file)
    assert result.dict(exclude={"generator"}) == {
        "datahash": "1e20344474d5a2ba3451baeba1565b3932f369980f32d705617020a11f7817bd56c9",
        "filename": "image.svg",
        "filesize": 155,
        "iscc": "ISCC:KUAPHHVHTGLKQFQ3GRCHJVNCXI2FC",
        "mediatype": "image/svg+xml",
    }
