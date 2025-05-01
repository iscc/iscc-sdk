import pytest
import iscc_sdk as idk


# Skip tests if packages are not installed
sci_installed = idk.is_installed("iscc_sci")
sct_installed = idk.is_installed("iscc_sct")


@pytest.mark.skipif(sci_installed, reason="iscc-sci is installed")
def test_code_image_semantic_raises(doc_file):
    with pytest.raises(idk.EnvironmentError):
        idk.code_image_semantic(doc_file)


@pytest.mark.skipif(sct_installed, reason="iscc-sct is installed")
def test_code_text_semantic_raises(doc_file):
    with pytest.raises(idk.EnvironmentError):
        idk.code_text_semantic(doc_file)


@pytest.mark.skipif(not sci_installed, reason="iscc-sci not installed")
def test_code_image_semantic(jpg_file):
    assert idk.code_image_semantic(jpg_file).dict() == {"iscc": "ISCC:CEAQYWTPK2Q7ZTK4"}


@pytest.mark.skipif(not sct_installed, reason="iscc-sct not installed")
def test_code_text_semantic(doc_file):
    assert idk.code_text_semantic(doc_file).dict() == {
        "iscc": "ISCC:CAA7X3SMP7IQ4Z65",
        "characters": 6068,
    }


@pytest.mark.skipif(not sct_installed, reason="iscc-sct not installed")
def test_code_iscc_with_semantic_text(doc_file, monkeypatch):
    monkeypatch.setattr(idk.sdk_opts, "experimental", True)
    assert idk.code_iscc(doc_file).dict() == {
        "@type": "TextDigitalDocument",
        "iscc": "ISCC:KADV5NAQXBCHCWFW7PXEY76RBZT52BQETCAX3TX4N6BSAWE3WOCUAC2G2HV5MT2RKNYQ",
        "metahash": "1e201da548c5285ed35f293c3e22c2f050e037643aae8cf9244b532a162ff5031f52",
        "datahash": "1e2046d1ebd64f515371c88d1df5bc0d43893b1fa1e58654b2c4244e491d06007a61",
        "name": "title from metadata",
        "filename": "text.doc",
        "filesize": 40448,
        "mode": "text",
        "mediatype": "application/msword",
        "characters": 4951,
        "creator": "titusz",
        "generator": "iscc-sdk - v0.8.2",
    }


@pytest.mark.skipif(not sct_installed, reason="iscc-sct not installed")
def test_code_iscc_with_semantic_text_granular(doc_file, monkeypatch):
    import iscc_sct as sct

    monkeypatch.setattr(idk.sdk_opts, "experimental", True)
    monkeypatch.setattr(idk.sdk_opts, "granular", True)
    monkeypatch.setattr(sct.sct_opts, "bits", 256)
    monkeypatch.setattr(sct.sct_opts, "bits_granular", 256)
    monkeypatch.setattr(sct.sct_opts, "simprints", True)
    monkeypatch.setattr(sct.sct_opts, "offsets", True)
    monkeypatch.setattr(sct.sct_opts, "sizes", True)
    monkeypatch.setattr(sct.sct_opts, "byte_offsets", True)
    assert idk.code_iscc(doc_file).dict() == {
        "@type": "TextDigitalDocument",
        "iscc": "ISCC:KADV5NAQXBCHCWFW7PXEY76RBZT52BQETCAX3TX4N6BSAWE3WOCUAC2G2HV5MT2RKNYQ",
        "metahash": "1e201da548c5285ed35f293c3e22c2f050e037643aae8cf9244b532a162ff5031f52",
        "datahash": "1e2046d1ebd64f515371c88d1df5bc0d43893b1fa1e58654b2c4244e491d06007a61",
        "name": "title from metadata",
        "filename": "text.doc",
        "filesize": 40448,
        "generator": "iscc-sdk - v0.8.2",
        "mediatype": "application/msword",
        "mode": "text",
        "characters": 4951,
        "creator": "titusz",
        "features": [
            {
                "maintype": "semantic",
                "subtype": "text",
                "version": 0,
                "byte_offsets": True,
                "simprints": [
                    "XUj8aOg4CGm5Uosm-Ggxi7d9G9pa4NBMyBDDAhrkf00",
                    "--5Of_EKZ90ywJCOFeXNmqGGhMpMTI9djU4WWlGN0dY",
                    "--5Of_EKZ90ywJCOFeXNmqGGhMpMTI9djU4WWlGN0dY",
                    "865-e3EKZ90ywBCONeXNmqGChMpMTI9dDU4eWlCL0dY",
                    "--9K9-EeZ912CICDN3QLmrGG3s5NTIVdjy4fSliNk-I",
                    "4-5I70E8Z90yNoiDlzULmmDG3s4NXodVjy4WWliMk0I",
                    "8-9K_9E8Z91zaICCl3ULmzTG3u4MXoddjw4WWkGMkcY",
                    "86pvUlEOZ90ywIDqH-WNiuGCxspNTI9cjU4WWlCP0VY",
                    "c6p_VlEOZ90ywIDqH-SNiuGCxspNTI9cjU4WWlCP0VY",
                    "82dsL9FKZ9wyyDGGlS2NuiGGhGpcbg9ZTU4eWkmN1dI",
                    "-6pe_9EKZ90y4JCOFeWNmqGCxMpNTItdDU4eWlCP0dY",
                    "--5Of_EKZ90ywJCOFeXNmqGGhMpMTI9djU4WWlGN0dY",
                    "865-e3EKZ90yYBCOP-XNmqGChMpMTI9cDU4eWlGL0dY",
                    "--5Of_EKZ90ywJCOFeXNmqGGhMpMTI9djU4WWlGN0dY",
                    "--5Of_EKZ90ywJCOFeXNmqGGhMpMTI9djU4WWlGN0dY",
                    "865-e3EKZ90ywBCONeXNmqGChMpMTI9dDU4eWlCL0dY",
                    "--9K9-EeZ912CICDN3QLmrGG3s5NTIVdjy4fSliNk-I",
                    "4-5I70E8Z90yNoiDlzULmmDG3s4NXodVjy4WWliMk0I",
                    "8-9K_9E8Z91z4IGClH0LmjTG3u4MXoddjw4WWkGMkcY",
                ],
                "offsets": [
                    0,
                    19,
                    315,
                    611,
                    907,
                    1325,
                    1726,
                    2262,
                    2558,
                    2994,
                    3133,
                    3401,
                    3697,
                    3964,
                    4260,
                    4556,
                    4852,
                    5270,
                    5671,
                ],
                "sizes": [
                    19,
                    452,
                    452,
                    298,
                    420,
                    403,
                    536,
                    436,
                    436,
                    139,
                    424,
                    452,
                    267,
                    452,
                    452,
                    298,
                    420,
                    403,
                    397,
                ],
            },
            {
                "maintype": "content",
                "subtype": "text",
                "version": 0,
                "byte_offsets": False,
                "simprints": [
                    "k5TpwXVE3j9N5IBxm36c4hkXP6fHOv8bkY2f68_8XSg",
                    "OERRAF2u5WWuLHZLZzgcCSoCoL9R0NYrBJD7s7A43t0",
                    "AARYEMzu5WEOfTZq5ixNLcoThJ5AgJYNRICysqEs3v0",
                    "lp6NgXnE_C1c6ij12-w04RwZN4XJyP0KgIrbKYX81yo",
                    "OERRAF2u5WWuLHZLZzgcCSoCoL9R0NYrBJD7s7A43t0",
                    "AARYEMzu5WEOfTZq5ixNLcoThJ5AgJYNRICysqEs3v0",
                    "JfC6tnH1BuHFMviS2deReiUuelIIMvWWOozU6afjErU",
                ],
                "offsets": [0, 996, 1453, 2122, 4941, 5398, 6067],
                "sizes": [996, 457, 669, 2819, 457, 669, 1],
            },
        ],
    }


@pytest.mark.skipif(not sci_installed, reason="iscc-sci not installed")
def test_code_iscc_with_semantic_image(png_file, monkeypatch):
    monkeypatch.setattr(idk.sdk_opts, "experimental", True)
    assert idk.code_iscc(png_file).dict() == {
        "@type": "ImageObject",
        "creator": "Another Cat Lover",
        "datahash": "1e20feb85f1709f51ebf31c2feab2092a61826da36cc79eddc4cb04800b47db146a6",
        "filename": "img.png",
        "filesize": 54595,
        "generator": "iscc-sdk - v0.8.2",
        "height": 133,
        "iscc": "ISCC:KEDSR5352MR7TNV4BVNG6VVB7TGVZQ2DGCPDZHUOM55CG2YTPY75IZH6XBPROCPVD27Q",
        "mediatype": "image/png",
        "metahash": "1e2011dfae49dd718631175cbb05a9c459d19a25556ff3c03692bc3a5fc87c623740",
        "mode": "image",
        "name": "Concentrated Cat PNG",
        "thumbnail": "data:image/webp;base64,UklGRsYFAABXRUJQVlA4ILoFAABwIgCdASqAAFUAPxFyr1KsJiQnrhkqYYAiCWcA0NO4SzE4K729xs0KGE3TPf58LAwDWfcLC3d0xi8kjSpMSal8MME9Dkc7+SfOysASz0517nKQJQhJnjLjM10EuxQsO338neNVD0h5ihTyOGuaMBa/aF0wgoQq+uBaGlVXrTlFOF08iTVVbRj+9f60o2MbQWOKnWpQfydPftRmdXgnBdZu/z/lqnnGCHlDJNr1t80zujPSolLYAodnFkiUYGrQMuMGCtJz5/D4JUvMF7mZ2vowhrj3N6BwAuxgfcX97HkmQIeYl3C3eg7dOoufvW24Am/i/iMmS6XnCMW3gbiN9S/4dTYJ/ZPa/dXE2Gz9dIFkEa/tYyQ418LhlQwh3AD+9xtO0Qfk17nyoJMFdziQFPZz1KYYlpfULSDIgbTRRDlGGBMi6k6nsi7OsQ0j1rnQhfua79tMCfO3jFeMoB4REOpkALW6V2ZpUYblhFqY/ZzM5twYPP1hNi33QUFwQP+oAFPSyfU4lV2YFN0Be5mqSvPsDrUBhI7XWr6R0xU9GEVSGqhPBEs69ysg2BaigCpHFOcqw+VrLtsISCI39BX55LdkTGcjnf6/QTBxHXtJ2M6duEKYl3sRWiMh4w1ma2JPqowcUuttr6czP4xMR4C39UViot0K+L9Fqzm+P8u4ezUqjX0VyKiFb8WEHm7/m7vBz5bwjE/F3t7AWzozfC2BWpggw6eCNloMT3+Qkf1wPMTg3REesutDjJG9vOc8Eu0pJgmIr4GJJNeiDCkJzZ/MZKO1XW7smwZiCK9Rp11+Nm8og35M02IXMdR/baDex1KB1zDCFCAPnPWtkzhr0pEDZ8EOb47Bh6sk7IGVWxjHpgRhSyEp+WacIMw00FNVhp7xvKgTcvCSBX2rTxmQv5K8Uku2Jk+Jp4AiQ2+NVWb311HTfifFcxOtKluSEZ3n4/WCFe+fvtCVjTzfR6fUlrUmFXQrDWLWXTep+ohjKhFL7vZKiMezMygeqfn2uztDMaI0xTDM2UrOCBNLBso/tMxB63aa3QsM+sfAl7gJfT16L62WgxNHf3QyYBaA465pYSNx5p5K72bosKtt1DZMJlrHczWNbrt+5nerLrTxcWVvU4IZ4ioezwuOgiakg7JkPZ72OMcoomVYiy6WgLLlfx4Sd786L+ppyAkpXOw1EDi8CTPhNwLoDhKtcgAMsuxrFZ46kMoZ5G7Pd8axW+/RR0IGDbHPSj9bjAK3SCxKMG/NVcApdR2atgYR49K+D7mZtTriKTlLR258TynrkZlYtJgyKFCF9TofxOCMD9x74az6M2Ohof2aXwKYtSkoISostsbddNgDvbhl6LM9GNHUoF2yxjGBzzI0BppJ6ZINh+oYSPLhepzoTqK+3Dayyk6vCRv56twMXTkZ5MOk9NPTGrpbnLjR9MpbeEqQrYP9UL8qbyIU9oduNJfQjdT1gz9ciSKSqXErzVqxJNrKIZzSyhbgzjJ/tgUntGTpiXJE5+xAGiiDTG4jQiZ7aTYzYCoxuRTt8qB2X7ZjyJdnLjtD+1TckrSKmtkjdEjNIams8jZgxJq0u16TQHS3lbrOTfLkKYD8JApK/d6rrl4i99Nxg71s4LAmIlVA26V1lBcUADlZHalf8dMiu1AkBH0+vzweOGSuWDXyasCCA1Hb1iNadLefcG5dyuGlawoGIdlOWz1fgiAbuF0i15lv0TFMzvJo6eL8A1FgnGJS9F4F25aRZ32Q7ACUfDif7bN4aUdUlpRsUIom4LjAbGSDrhYfVCPE4C+f0aaXtvjyJwdQgPPyoXKrkApy5+rzsfW3iOR/A0tu4/dG9Sug5QHOgS8MccWkaxtAIGSDUWOhkTTPHMZn/zyJH8HkpMALTdSsEQJW5j8kfh7pAeHoQJOp4TrazFJ1aJo1iReTFUge0uNHQnuZmFPYF7rAdFUkF0FNogAAAA==",
        "width": 200,
    }
