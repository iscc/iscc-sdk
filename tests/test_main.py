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
        "thumbnail": "data:image/avif;base64,AAAAIGZ0eXBhdmlmAAAAAGF2aWZtaWYxbWlhZk1BMUIAAADrbWV0YQAAAAAAAAAhaGRscgAAAAAAAAAAcGljdAAAAAAAAAAAAAAAAAAAAAAOcGl0bQAAAAAAAQAAAB5pbG9jAAAAAEQAAAEAAQAAAAEAAAETAAABKgAAAChpaW5mAAAAAAABAAAAGmluZmUCAAAAAAEAAGF2MDFDb2xvcgAAAABqaXBycAAAAEtpcGNvAAAAFGlzcGUAAAAAAAAAYwAAAIAAAAAQcGl4aQAAAAADCAgIAAAADGF2MUOBAAwAAAAAE2NvbHJuY2x4AAEADQAGgAAAABdpcG1hAAAAAAAAAAEAAQQBAoMEAAABMm1kYXQSAAoJGBmxf2CAhoNCMpoCEsAGmmmhQNf/L/e3W6TabotwWOQlagjMec2TnUJHVMoUHxLIBge5X2OCRmha+hWg8apuUHNRF47mk9cS/N/OG0JsWPP61cIobrXW5QbJJtIH90SS9eF+u9WF6F1lFkHNH60HaGC+se5f3gDlDz6WXwnw5E9tt/ez4vBAAC3nZznyS+W141AWfNHwn5G1rhzqcSBBhviS11Yy+BlRDq3MkwRsMVJjFAGad2n2zgQ/2gu76cMkIGrA/li2kYIgggf1ixEI/MZ1X5q+tkAjZbxBN0ZZuFDAeTOTARTNN5Nd3/0SmicYs5MoWdcLzqctizVM82xxxWZkoJ0ev2NEs9T7mUtsujKypdBAzv2kqU9TWQWL47+8u92XEj+b",
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
        "thumbnail": "data:image/avif;base64,AAAAIGZ0eXBhdmlmAAAAAGF2aWZtaWYxbWlhZk1BMUIAAADrbWV0YQAAAAAAAAAhaGRscgAAAAAAAAAAcGljdAAAAAAAAAAAAAAAAAAAAAAOcGl0bQAAAAAAAQAAAB5pbG9jAAAAAEQAAAEAAQAAAAEAAAETAAAD4wAAAChpaW5mAAAAAAABAAAAGmluZmUCAAAAAAEAAGF2MDFDb2xvcgAAAABqaXBycAAAAEtpcGNvAAAAFGlzcGUAAAAAAAAAgAAAAFUAAAAQcGl4aQAAAAADCAgIAAAADGF2MUOBAAwAAAAAE2NvbHJuY2x4AAEADQAGgAAAABdpcG1hAAAAAAAAAAEAAQQBAoMEAAAD621kYXQSAAoJGBm/1GCAhoNCMtMHEsAGmmmhQNgPaOHK3Lj4IJC+2rSLcjjQ6qSa4Sh3PN7wDJQdnP4z0vquxHHludIpO/Cxi6W710N0mwqxqZyvKF1OmdyNOlWi97YF9s1FFaoHfPGogO2U0PmaCY8zZn813I4m+hPJI1bHzhcHXPlcZtkt7506ED1O2LfjfLMpcda/S1LYthDkK0UmrgLuVz/GAzxVXee6U8FS3QCvmVTSi4Vm9z0XQQbqlv50v4dO0RC5Sx0k+T+SHvQU07sTfUE07F63X02KkA8Kd2QWsQkE8Dt6wqoLIUPNCD+z0RPVQ40UXX/HkvYMdR+p8lZOXOvgtDDvA7yPVctWLp1a3DMBTUKyxRUQaqNxdkmonaYJqQnmGi+C1EP0PNuAj8evWbtQlQHyPq8Ek5kTcrqowGvx/1vvzDxGvf+uM/wMiVTwXjaQQv+uwS69N8P+Fpkov5VjHYVWSyDIPvfFnBl3XIKPr6nOeCjJRE2AirGhxSqvIHAYuPPPQVGRxmpjlNq/Z0saQn7iP6FO3sz1Xd6Q8DXHzlVJeNEP4pmy524Lae1xvZnaFbBBKyQYFzfsLMcxWzMGKNYHY+vyfv0obGaIUXMrQlEpATCdhlpF9DQxqWNj0zWukqaCa7saKZGdJYpZNYcv0kM8t+RIRM7opVRPmbKbldfGDWgomWzUieJMFUDSmoqUNK260lzgFrIJphzcojNPEz12eQpuOE3fxcFuvnEINfqSDCQcNWle1gqeH2AWO/cGhPIxk09MBsm8b4388LECpiIgbPOZDHZapM/I70wVvXgD8i5N5y7ZjsEZnvoD5OCCQVHQBfUqCseK5tW7RgdwMI/3fYbUo4zsF2612dUG/um5VkjaeQljvI5j7MNo5E+7le9qWBxJ46T88PVcL4UKLo0/dJZR0LFZg4LIlJNLVxRr2YFcQ/DfSL7Pu1JkhNZl2vzCzQzGwVTbdaQA6F2GCXfo0s2TtVZhv6sZmrxKOeCWMcu813YchoCWrnqcvCtgnhH7WTNuKEsU7x3/Ueo6BDUk5EYkAqKXL7b898pgDYj9jss7PqvnIC99sDMB5B2GfcOdIC6I/E/wzfaarUftFdlRK9C+c2DxsxlG7GsLwZ8IItkJ6nPdhdZeFg02xT81hQX0Q23IvCNdXnFbZkoWyPZ9O/VnuN2CezFmISCgQg4e6NVWQfWDoPRf0eYGfPVp/yICJzMviFvnMQmfw5MX8ZyrmFVB6yHmq0lCTjRPuII27xMrtGP/NK1v9iac5xQqwFvgIMbSxjYG6ULWWyI4BvABd6W5HSnsm/Zj/ly13N1MQA==",
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
        "thumbnail": "data:image/avif;base64,AAAAIGZ0eXBhdmlmAAAAAGF2aWZtaWYxbWlhZk1BMUIAAADrbWV0YQAAAAAAAAAhaGRscgAAAAAAAAAAcGljdAAAAAAAAAAAAAAAAAAAAAAOcGl0bQAAAAAAAQAAAB5pbG9jAAAAAEQAAAEAAQAAAAEAAAETAAAC7wAAAChpaW5mAAAAAAABAAAAGmluZmUCAAAAAAEAAGF2MDFDb2xvcgAAAABqaXBycAAAAEtpcGNvAAAAFGlzcGUAAAAAAAAAgAAAAGkAAAAQcGl4aQAAAAADCAgIAAAADGF2MUOBAAwAAAAAE2NvbHJuY2x4AAEADQAGgAAAABdpcG1hAAAAAAAAAAEAAQQBAoMEAAAC921kYXQSAAoJGBm/6GCAhoNCMt8FEsAGmmmhQMDG716C2A8FXBnDXkzTk8f9O226jtkCbR4My8RBxMdPZr75HsJHkKGQ9/mJO89Fb+y+xDreyUkbG4/pgfYNIFh/F1vIx+geZVIV2PfWOKXCH5v/UZ148kXMKfFdiGNdn4ln6IAvFnk+S2lSbKlINamWwjjgtJrXnuNgD3TmCYpaBT9pFhn0ImyzdR3m4WiY/19QqsIg8mgARYY7f5KM1y2mxk6gZw40C3XTKWvUcfN3sZDm7uPHxQeNny8A2e1vThPM10vPp/61uWCJG5KY/+s39WxoPaTzT5kMvHzkOO+GgeABO/1Nbw/KCZ6MIYEwpZ0Dz4uyHpZFzmCWQmYW4WZd9Qgvvf2I06e/ZHwL+66MOv86V4ufLhSuc8qYHAHoZrj19+LAtp4tXPkbNcUXGBiC09Qwj5J5X8CC6hv+sboEu2mRu0uICZzLq/GKrIk/j5dccnrJJ6I5m1fN5j/7+IPAGblJGwGqgetZhpjVocMTbwnmbdN1HSjr1xK0ADEPWAZcToSWBIMnKoaeV94hwKbc3ZX5EJnfSpg3rBw38qtxRz/itL2VDlj6X8UgOQIXFeLD+5j6X8t7RpVnH43whqReDNQ8ac9/FQRJ90Fx0ME8vk1LFeTgAGsCzQ6Ot6O7AAztPXO7MZfK9CQFc8rQmYqlI88lYxUHA+r90w60IYbydIO+jj9lt9Yb7KScoiGMYgaYAixJLIoUFNGPwj5CVTH7HydwlEnaX0AsBuyyNW+xDOt9Mx6MYS5ji7+sjs2JRDhenEZKJlT3OcvR6OJRb9s48gbvbC+cJh9g4fzJ3WOpI8A43W044AUa1MKaM4JY8zXK5arI4BbU1U46vmpBYzeckplsh+qx3k8OV/36W+kjZZvQc3G+oe6ATx/zUrLHFMWWzdnxB5LeieFZBvn0koTZs7tLlbwOsIX+rwuEqo/SJcWBD3Q7I7qV/8cLP9/mW9zwCjbkqsOZ",
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
        "thumbnail": "data:image/avif;base64,AAAAIGZ0eXBhdmlmAAAAAGF2aWZtaWYxbWlhZk1BMUIAAADrbWV0YQAAAAAAAAAhaGRscgAAAAAAAAAAcGljdAAAAAAAAAAAAAAAAAAAAAAOcGl0bQAAAAAAAQAAAB5pbG9jAAAAAEQAAAEAAQAAAAEAAAETAAAD4wAAAChpaW5mAAAAAAABAAAAGmluZmUCAAAAAAEAAGF2MDFDb2xvcgAAAABqaXBycAAAAEtpcGNvAAAAFGlzcGUAAAAAAAAAgAAAAFUAAAAQcGl4aQAAAAADCAgIAAAADGF2MUOBAAwAAAAAE2NvbHJuY2x4AAEADQAGgAAAABdpcG1hAAAAAAAAAAEAAQQBAoMEAAAD621kYXQSAAoJGBm/1GCAhoNCMtMHEsAGmmmhQNgPaOHK3Lj4IJC+2rSLcjjQ6qSa4Sh3PN7wDJQdnP4z0vquxHHludIpO/Cxi6W710N0mwqxqZyvKF1OmdyNOlWi97YF9s1FFaoHfPGogO2U0PmaCY8zZn813I4m+hPJI1bHzhcHXPlcZtkt7506ED1O2LfjfLMpcda/S1LYthDkK0UmrgLuVz/GAzxVXee6U8FS3QCvmVTSi4Vm9z0XQQbqlv50v4dO0RC5Sx0k+T+SHvQU07sTfUE07F63X02KkA8Kd2QWsQkE8Dt6wqoLIUPNCD+z0RPVQ40UXX/HkvYMdR+p8lZOXOvgtDDvA7yPVctWLp1a3DMBTUKyxRUQaqNxdkmonaYJqQnmGi+C1EP0PNuAj8evWbtQlQHyPq8Ek5kTcrqowGvx/1vvzDxGvf+uM/wMiVTwXjaQQv+uwS69N8P+Fpkov5VjHYVWSyDIPvfFnBl3XIKPr6nOeCjJRE2AirGhxSqvIHAYuPPPQVGRxmpjlNq/Z0saQn7iP6FO3sz1Xd6Q8DXHzlVJeNEP4pmy524Lae1xvZnaFbBBKyQYFzfsLMcxWzMGKNYHY+vyfv0obGaIUXMrQlEpATCdhlpF9DQxqWNj0zWukqaCa7saKZGdJYpZNYcv0kM8t+RIRM7opVRPmbKbldfGDWgomWzUieJMFUDSmoqUNK260lzgFrIJphzcojNPEz12eQpuOE3fxcFuvnEINfqSDCQcNWle1gqeH2AWO/cGhPIxk09MBsm8b4388LECpiIgbPOZDHZapM/I70wVvXgD8i5N5y7ZjsEZnvoD5OCCQVHQBfUqCseK5tW7RgdwMI/3fYbUo4zsF2612dUG/um5VkjaeQljvI5j7MNo5E+7le9qWBxJ46T88PVcL4UKLo0/dJZR0LFZg4LIlJNLVxRr2YFcQ/DfSL7Pu1JkhNZl2vzCzQzGwVTbdaQA6F2GCXfo0s2TtVZhv6sZmrxKOeCWMcu813YchoCWrnqcvCtgnhH7WTNuKEsU7x3/Ueo6BDUk5EYkAqKXL7b898pgDYj9jss7PqvnIC99sDMB5B2GfcOdIC6I/E/wzfaarUftFdlRK9C+c2DxsxlG7GsLwZ8IItkJ6nPdhdZeFg02xT81hQX0Q23IvCNdXnFbZkoWyPZ9O/VnuN2CezFmISCgQg4e6NVWQfWDoPRf0eYGfPVp/yICJzMviFvnMQmfw5MX8ZyrmFVB6yHmq0lCTjRPuII27xMrtGP/NK1v9iac5xQqwFvgIMbSxjYG6ULWWyI4BvABd6W5HSnsm/Zj/ly13N1MQA==",
        "width": 200,
    }


def test_code_text(docx_file):
    assert idk.code_text(docx_file).dict() == {
        "iscc": "ISCC:EAAQMBEYQF6457DP",
        "name": "title from metadata",
        "creator": "titusz",
        "characters": 4951,
    }


def test_code_text_granular(docx_file):
    idk.sdk_opts.granular = True
    assert idk.code_text(docx_file).dict() == {
        "iscc": "ISCC:EAAQMBEYQF6457DP",
        "name": "title from metadata",
        "creator": "titusz",
        "characters": 4951,
        "features": [
            {
                "kind": "text",
                "version": 0,
                "features": ["BgSYgX3O_G8"],
                "sizes": [6069],
            }
        ],
    }
    idk.sdk_opts.granular = False


def test_code_image(jpg_file):
    assert idk.code_image(jpg_file).dict() == {
        "creator": "Some Cat Lover",
        "height": 133,
        "iscc": "ISCC:EEA4GQZQTY6J5DTH",
        "name": "Concentrated Cat",
        "thumbnail": "data:image/avif;base64,AAAAIGZ0eXBhdmlmAAAAAGF2aWZtaWYxbWlhZk1BMUIAAADrbWV0YQAAAAAAAAAhaGRscgAAAAAAAAAAcGljdAAAAAAAAAAAAAAAAAAAAAAOcGl0bQAAAAAAAQAAAB5pbG9jAAAAAEQAAAEAAQAAAAEAAAETAAAD4wAAAChpaW5mAAAAAAABAAAAGmluZmUCAAAAAAEAAGF2MDFDb2xvcgAAAABqaXBycAAAAEtpcGNvAAAAFGlzcGUAAAAAAAAAgAAAAFUAAAAQcGl4aQAAAAADCAgIAAAADGF2MUOBAAwAAAAAE2NvbHJuY2x4AAEADQAGgAAAABdpcG1hAAAAAAAAAAEAAQQBAoMEAAAD621kYXQSAAoJGBm/1GCAhoNCMtMHEsAGmmmhQNgPaOHK3Lj4IJC+2rSLcjjQ6qSa4Sh3PN7wDJQdnP4z0vquxHHludIpO/Cxi6W710N0mwqxqZyvKF1OmdyNOlWi97YF9s1FFaoHfPGogO2U0PmaCY8zZn813I4m+hPJI1bHzhcHXPlcZtkt7506ED1O2LfjfLMpcda/S1LYthDkK0UmrgLuVz/GAzxVXee6U8FS3QCvmVTSi4Vm9z0XQQbqlv50v4dO0RC5Sx0k+T+SHvQU07sTfUE07F63X02KkA8Kd2QWsQkE8Dt6wqoLIUPNCD+z0RPVQ40UXX/HkvYMdR+p8lZOXOvgtDDvA7yPVctWLp1a3DMBTUKyxRUQaqNxdkmonaYJqQnmGi+C1EP0PNuAj8evWbtQlQHyPq8Ek5kTcrqowGvx/1vvzDxGvf+uM/wMiVTwXjaQQv+uwS69N8P+Fpkov5VjHYVWSyDIPvfFnBl3XIKPr6nOeCjJRE2AirGhxSqvIHAYuPPPQVGRxmpjlNq/Z0saQn7iP6FO3sz1Xd6Q8DXHzlVJeNEP4pmy524Lae1xvZnaFbBBKyQYFzfsLMcxWzMGKNYHY+vyfv0obGaIUXMrQlEpATCdhlpF9DQxqWNj0zWukqaCa7saKZGdJYpZNYcv0kM8t+RIRM7opVRPmbKbldfGDWgomWzUieJMFUDSmoqUNK260lzgFrIJphzcojNPEz12eQpuOE3fxcFuvnEINfqSDCQcNWle1gqeH2AWO/cGhPIxk09MBsm8b4388LECpiIgbPOZDHZapM/I70wVvXgD8i5N5y7ZjsEZnvoD5OCCQVHQBfUqCseK5tW7RgdwMI/3fYbUo4zsF2612dUG/um5VkjaeQljvI5j7MNo5E+7le9qWBxJ46T88PVcL4UKLo0/dJZR0LFZg4LIlJNLVxRr2YFcQ/DfSL7Pu1JkhNZl2vzCzQzGwVTbdaQA6F2GCXfo0s2TtVZhv6sZmrxKOeCWMcu813YchoCWrnqcvCtgnhH7WTNuKEsU7x3/Ueo6BDUk5EYkAqKXL7b898pgDYj9jss7PqvnIC99sDMB5B2GfcOdIC6I/E/wzfaarUftFdlRK9C+c2DxsxlG7GsLwZ8IItkJ6nPdhdZeFg02xT81hQX0Q23IvCNdXnFbZkoWyPZ9O/VnuN2CezFmISCgQg4e6NVWQfWDoPRf0eYGfPVp/yICJzMviFvnMQmfw5MX8ZyrmFVB6yHmq0lCTjRPuII27xMrtGP/NK1v9iac5xQqwFvgIMbSxjYG6ULWWyI4BvABd6W5HSnsm/Zj/ly13N1MQA==",
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
        "thumbnail": "data:image/avif;base64,AAAAIGZ0eXBhdmlmAAAAAGF2aWZtaWYxbWlhZk1BMUIAAADrbWV0YQAAAAAAAAAhaGRscgAAAAAAAAAAcGljdAAAAAAAAAAAAAAAAAAAAAAOcGl0bQAAAAAAAQAAAB5pbG9jAAAAAEQAAAEAAQAAAAEAAAETAAAC7wAAAChpaW5mAAAAAAABAAAAGmluZmUCAAAAAAEAAGF2MDFDb2xvcgAAAABqaXBycAAAAEtpcGNvAAAAFGlzcGUAAAAAAAAAgAAAAGkAAAAQcGl4aQAAAAADCAgIAAAADGF2MUOBAAwAAAAAE2NvbHJuY2x4AAEADQAGgAAAABdpcG1hAAAAAAAAAAEAAQQBAoMEAAAC921kYXQSAAoJGBm/6GCAhoNCMt8FEsAGmmmhQMDG716C2A8FXBnDXkzTk8f9O226jtkCbR4My8RBxMdPZr75HsJHkKGQ9/mJO89Fb+y+xDreyUkbG4/pgfYNIFh/F1vIx+geZVIV2PfWOKXCH5v/UZ148kXMKfFdiGNdn4ln6IAvFnk+S2lSbKlINamWwjjgtJrXnuNgD3TmCYpaBT9pFhn0ImyzdR3m4WiY/19QqsIg8mgARYY7f5KM1y2mxk6gZw40C3XTKWvUcfN3sZDm7uPHxQeNny8A2e1vThPM10vPp/61uWCJG5KY/+s39WxoPaTzT5kMvHzkOO+GgeABO/1Nbw/KCZ6MIYEwpZ0Dz4uyHpZFzmCWQmYW4WZd9Qgvvf2I06e/ZHwL+66MOv86V4ufLhSuc8qYHAHoZrj19+LAtp4tXPkbNcUXGBiC09Qwj5J5X8CC6hv+sboEu2mRu0uICZzLq/GKrIk/j5dccnrJJ6I5m1fN5j/7+IPAGblJGwGqgetZhpjVocMTbwnmbdN1HSjr1xK0ADEPWAZcToSWBIMnKoaeV94hwKbc3ZX5EJnfSpg3rBw38qtxRz/itL2VDlj6X8UgOQIXFeLD+5j6X8t7RpVnH43whqReDNQ8ac9/FQRJ90Fx0ME8vk1LFeTgAGsCzQ6Ot6O7AAztPXO7MZfK9CQFc8rQmYqlI88lYxUHA+r90w60IYbydIO+jj9lt9Yb7KScoiGMYgaYAixJLIoUFNGPwj5CVTH7HydwlEnaX0AsBuyyNW+xDOt9Mx6MYS5ji7+sjs2JRDhenEZKJlT3OcvR6OJRb9s48gbvbC+cJh9g4fzJ3WOpI8A43W044AUa1MKaM4JY8zXK5arI4BbU1U46vmpBYzeckplsh+qx3k8OV/36W+kjZZvQc3G+oe6ATx/zUrLHFMWWzdnxB5LeieFZBvn0koTZs7tLlbwOsIX+rwuEqo/SJcWBD3Q7I7qV/8cLP9/mW9zwCjbkqsOZ",
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
        "thumbnail": "data:image/avif;base64,AAAAIGZ0eXBhdmlmAAAAAGF2aWZtaWYxbWlhZk1BMUIAAADrbWV0YQAAAAAAAAAhaGRscgAAAAAAAAAAcGljdAAAAAAAAAAAAAAAAAAAAAAOcGl0bQAAAAAAAQAAAB5pbG9jAAAAAEQAAAEAAQAAAAEAAAETAAAD4wAAAChpaW5mAAAAAAABAAAAGmluZmUCAAAAAAEAAGF2MDFDb2xvcgAAAABqaXBycAAAAEtpcGNvAAAAFGlzcGUAAAAAAAAAgAAAAFUAAAAQcGl4aQAAAAADCAgIAAAADGF2MUOBAAwAAAAAE2NvbHJuY2x4AAEADQAGgAAAABdpcG1hAAAAAAAAAAEAAQQBAoMEAAAD621kYXQSAAoJGBm/1GCAhoNCMtMHEsAGmmmhQNgPaOHK3Lj4IJC+2rSLcjjQ6qSa4Sh3PN7wDJQdnP4z0vquxHHludIpO/Cxi6W710N0mwqxqZyvKF1OmdyNOlWi97YF9s1FFaoHfPGogO2U0PmaCY8zZn813I4m+hPJI1bHzhcHXPlcZtkt7506ED1O2LfjfLMpcda/S1LYthDkK0UmrgLuVz/GAzxVXee6U8FS3QCvmVTSi4Vm9z0XQQbqlv50v4dO0RC5Sx0k+T+SHvQU07sTfUE07F63X02KkA8Kd2QWsQkE8Dt6wqoLIUPNCD+z0RPVQ40UXX/HkvYMdR+p8lZOXOvgtDDvA7yPVctWLp1a3DMBTUKyxRUQaqNxdkmonaYJqQnmGi+C1EP0PNuAj8evWbtQlQHyPq8Ek5kTcrqowGvx/1vvzDxGvf+uM/wMiVTwXjaQQv+uwS69N8P+Fpkov5VjHYVWSyDIPvfFnBl3XIKPr6nOeCjJRE2AirGhxSqvIHAYuPPPQVGRxmpjlNq/Z0saQn7iP6FO3sz1Xd6Q8DXHzlVJeNEP4pmy524Lae1xvZnaFbBBKyQYFzfsLMcxWzMGKNYHY+vyfv0obGaIUXMrQlEpATCdhlpF9DQxqWNj0zWukqaCa7saKZGdJYpZNYcv0kM8t+RIRM7opVRPmbKbldfGDWgomWzUieJMFUDSmoqUNK260lzgFrIJphzcojNPEz12eQpuOE3fxcFuvnEINfqSDCQcNWle1gqeH2AWO/cGhPIxk09MBsm8b4388LECpiIgbPOZDHZapM/I70wVvXgD8i5N5y7ZjsEZnvoD5OCCQVHQBfUqCseK5tW7RgdwMI/3fYbUo4zsF2612dUG/um5VkjaeQljvI5j7MNo5E+7le9qWBxJ46T88PVcL4UKLo0/dJZR0LFZg4LIlJNLVxRr2YFcQ/DfSL7Pu1JkhNZl2vzCzQzGwVTbdaQA6F2GCXfo0s2TtVZhv6sZmrxKOeCWMcu813YchoCWrnqcvCtgnhH7WTNuKEsU7x3/Ueo6BDUk5EYkAqKXL7b898pgDYj9jss7PqvnIC99sDMB5B2GfcOdIC6I/E/wzfaarUftFdlRK9C+c2DxsxlG7GsLwZ8IItkJ6nPdhdZeFg02xT81hQX0Q23IvCNdXnFbZkoWyPZ9O/VnuN2CezFmISCgQg4e6NVWQfWDoPRf0eYGfPVp/yICJzMviFvnMQmfw5MX8ZyrmFVB6yHmq0lCTjRPuII27xMrtGP/NK1v9iac5xQqwFvgIMbSxjYG6ULWWyI4BvABd6W5HSnsm/Zj/ly13N1MQA==",
        "width": 200,
    }


def test_code_iscc_sum_fallback(svg_file):
    idk.sdk_opts.fallback = True
    result = idk.code_iscc(svg_file)
    assert result.dict(exclude={"generator"}) == {
        "datahash": "1e20344474d5a2ba3451baeba1565b3932f369980f32d705617020a11f7817bd56c9",
        "filename": "image.svg",
        "filesize": 155,
        "iscc": "ISCC:KUAPHHVHTGLKQFQ3GRCHJVNCXI2FC",
        "mediatype": "image/svg+xml",
    }
    idk.sdk_opts.fallback = False
