import iscc_sdk as idk


def test_code_iscc_text(pdf_file):
    assert idk.code_iscc(pdf_file).dict() == {
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
        "thumbnail": "data:image/webp;base64,UklGRhQEAABXRUJQVlA4IAgEAACwEgCdASpjAIAAPrVSo02nJKMiJ3O6yOAWiWkzjSC1C6Reznp+sQABFkPaZh/aCmUqsW/BvosW2KfVw78WmUc08wM8nb3c11VnfyGy2a5aPdfxHCQTwGxGweNMGzxm2Z2jEFxvqwoATFlrf9xo/VE9udn1Q64BAxos65LBrtLozEg6mat+LakDTH4PFrwm0iNqiFpj+d5x/j78PkCBoAD+mzFNArdTvG0MlL8f5xHy09tSKqt7ZSeBIkC2lH3a5AaDoVPZ5jMsa45MNylxorbH2vtxADmw+4dd0LTPmWhnHRkJg743JLiKmu+0bzJdA94R+Dn7RWfgZDzCOEHZe3gZbWZ86jnQC2zkbN/fM8rEkr/gchLKWfFwdMYUdal/UUnt6dpcaicpTobp/EWflri7XaZzzwbPHk8Llt8haeVIFH3WCjc1dnNZgfXx5frHq+VrCQehUo0e7YzWDIem/Cr8EI/w1AKAktrRTOiSKN4VWNBmVIxUuQxnggkMGAX7F3sLkJO7FteTvcdaX43fliwsQhHXDZVQrtHB2vQnRe0UrIitpYDrfNTHw1DGe6wSwmmuKYzqK9O4DhPpnTSMYLTo+Smk7lyWLKVZ/k4pjQIZjVxV8figTBhkwuHgy6iFYznLwqNbNWnqqwVVNDYbni1Rkh1G7fiCHls/dcTGcoXAfTNYtTWg2pYuX3SpCnhXd1srtjTiM8fkkLuQzbDaiDGB73x3Z5Q7AxxPUll+1PfShIkYFoAkMHxRGf/UwNLTxLyPEHANTzOLU9pe2v2gFw8bn3fpLi+4g2Sa7tbYokmCsCGxkVmbC2XtCy5Yz4tbXPleOXiSdp1/xGUzPt7Fw/vMpCn9p2isiA8IwWrPWzSYeXs7JNxkFC2TB3ImDqVfPYY2Dgnr0BGXB7WhpezYYIpRr5FOSnovqo1oCzSeISKwh5ZILvJwdQ0QTFC4swbu/jZJ43mceHYzThelI73a9Q5yLvtmYumUCTP99mPZdKkqR8axaTu+IAaD2utarTsmi+UXhKMmxGU+niTjV5tRughpnYN6s+QVsECiyXHwwj6/eqv/eW+RlW1cGYxSbVmQ790bv0NJ7enZnofBXTkU1YXw7bUS1c59iW73vB/csUjXJ4nD4MqUBjT/49uOytubyNDPYGflJ1LyaJDeZq3X686BvOHRYKkxOjGSoEhG3Jw0RFwftjb5z5Hf8KxPT/JBneRmdaOqXLkrM59e6eHAYBGPASHvzbnY6dBB0yl2dU2wq1oAa7WZ/kUnepjnFa54fudvh0jbpBHaUx++I+odeIaRr7FerRkLnTyqUIuGey8GNAakDAw+3twOnba3UVHgWM86HBqe68HxzBZZ6ykNwsz64ABCV5zgAAA=",
    }


def test_code_iscc_image(jpg_file):
    assert idk.code_iscc(jpg_file).dict() == {
        "@type": "ImageObject",
        "iscc": "ISCC:KECWRY3VY6R5SNV4YNBTBHR4T2HGP3HKVFO7TYUP2BKVFG724W63HVI",
        "creator": "Some Cat Lover",
        "datahash": "1e2055529bfae5bdb3d530c52f44d13ccd6a7c710f63620dc2db1c43c5592ae2dc97",
        "filesize": 35393,
        "filename": "img.jpg",
        "height": 133,
        "mediatype": "image/jpeg",
        "metahash": "1e209ce5052a03004657d8657167f53812718e9426d85b4cdd5106ef3d87412e6f64",
        "mode": "image",
        "name": "Concentrated Cat",
        "thumbnail": "data:image/webp;base64,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",
        "width": 200,
    }


def test_code_iscc_audio(mp3_file):
    assert idk.code_iscc(mp3_file).dict() == {
        "@type": "AudioObject",
        "iscc": "ISCC:KIC2JKSX7OH5PBIENISKEJTS4TRKHYJBCZDNLQXYILWJHQAP3N3KPTQ",
        "name": "Belly Button",
        "datahash": "1e20ec93c00fdb76a7cec587e4a2bddfa8d0a0bac8110d0c7130c351ea07c366d626",
        "duration": 15,
        "filesize": 225707,
        "filename": "audio.mp3",
        "mediatype": "audio/mpeg",
        "metahash": "1e20c4933dc8c03ea58568159a1cbfb04132c7db93b6b4cd025ffd4db37f52a4756f",
        "mode": "audio",
    }


def test_code_iscc_video(mp4_file):
    assert idk.code_iscc(mp4_file).dict() == {
        "@type": "VideoObject",
        "datahash": "1e209d412d76d9d516d07bb60f1ab3c1a5c1b176ed4f1cec94c96222a5d013ec3e38",
        "filename": "video.mp4",
        "filesize": 2161914,
        "iscc": "ISCC:KMCV6UK6BSXJ3I4GLYHIH5A5DNZPYBWQO33FNHPQFOOUCLLW3HKRNUA",
        "mediatype": "video/mp4",
        "metahash": "1e2096c0a53475a186ce37622aba7ba70651fc62cc8150f59eee6d17dc16d9bfbf25",
        "mode": "video",
        "name": "Kali by Anokato - Spiral Sessions 2019",
        "thumbnail": "data:image/webp;base64,UklGRkAFAABXRUJQVlA4IDQFAABQHACdASqAAGkAPrVUoU0nJL+iJds7o/AWiUAaVUmMC9Ymbvi4gI54bTdt50rwr7N+M3nP42/ab9zzG+k74b8n/VrvT9OHkr3QnKPB0+k/qr4qX8d6D/UjzQ/9N6a94N4t7AH8n/u3/R9lT+k8bP0p7Af66dcEw8O/Fjh0V9q/EzGIXOPxxGpc24WPN9p12h+zeDRpntIPLKARwz62m3BPGyFS9rzZiv3VJlg+hNKMMfZMQJzHYwM5pXOu/B8cvvwU0x4TrPQT/1NWb1QiI/XoZOGjVrAntgus6zRf5zFWbUxamLYiInReOWnQAP750EAB6/Gz7ppI6A3w/zt8U/tR4HwZILZiEJ39oTo6Jf1u3N4w7w0ALWz10zrZ8GVMOcoN7ib8ZG9jZz1xUfcW9Sdg0+9vgh5GLQpOT77rQTmy2vkPAmUpMeQOnCAYqmD8In78khGhd2PPfNzF5wjbMmcxmZr8pk0Tzza+jvY6twcoqfijYdYqRMT6BRQl95E1TQJ2vBWwn/5P406F/viJYID3/5Dl3LJlsmMlCDoIcd8zEtx+XLqcpUaER8pnGFbViIzy/0X3LvUkP9xlJzidkB3CgqYf26aIdunTUCYRLfeSpj2yptiOXx0YmRzx5XxrPm3i7GO2smpd6/o9ZIX9Q3vG20223jlv2Qrl2PToH2G91tWwDBpFLiyX+ojOGEyAtJ+PIxKoIxthBeved8lNoDHtsI2dur5AhYy0TVIwP0e6fQ0lsiHaEdU8AvOFGw5f/WaKrif6HjVbFKFQgEyBbFUQM8Xrykx3X8cKCq0EPcjj2ggd++n10yVCX4GSdB/Trerpf69HVhpJtMZLynD1z3cf9VI28q+1/LtCt8W7yI7GTekUoZaDEjALNUNT8ry/l9egi6aK59BAYWqvDgT8Vcu7hOiFL/qJBepaPtIUQkin19qvzT+9T0d8SGoG0binZs1UbMxY1phQeT3U16T17OxvcmhVnOV0C92EginYKqZw5n/xat/JbmptnAZP19BGkcOqnRCxVeJgwkxRB9vzu1xLM1i3Dt+WKXyv50lK4ykfU2srsOJHpSLgMz75gbyhEitaPiW49IooZ7Ae61bI6JMoI0N7kBDpFs8jOGXtczQBSAEtVe++l89JefzWcS2EH9Lmyk3+q7O0yHz2eE3KcImzXnN8AL/kcB0H28Y2q7WTRjGPg7qIzeg5rsuOBsSMstmMfGM1YDWb9k55rWvedKYcrQc4Tyc4uxLXOoZzfPfXVHO6sFJBw2DGX3n6sb8fegUVN+uxLKJnO4fkvw3aD6aamRI2lL1m3Z6YeRbIRkVAUbxu7QkFcfQ/NmygSImoYv96fjbxvoQLSMdaSj5ZCYYgx/J8n/XyeRaCsWAOeUqsx93z+Fq0JPrnOxm9ypga1WYQhn8RYnGjcd+y6uHoq7VAzXunweVYJGYMD5IDBZtaYCywWZHM2z5FtkzAlomZR173ct/Ls+p036ukw/nMbCKeHnkJ884g1xNf6Flzc7LRTA0H6Ttrz3rukIxtReTvlQ1FuI9QCxk3tVP9MzNrHhtwq85YHYLcgBopKZqMJxkCm62YZ+ckmErtGImje7dBmxlAZe290TV0R2vYx51znfnph4aLw6OiksjFM//JnYh/JEMYlTjl/v4LCa8qFgHQ/yPJql1BtdwmM9g3NkoL50nf/cOlQmSwljeE33QqAp0NwgkAlo7c3/LEib8gvzr+CHETvA4pAL1yMJfLDfxlG5U/+AeRF6lDsnZfKTDeUeZwAAAAAAA=",
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
        "iscc": "ISCC:AAA2JKSX7OH5PBIE",
        "name": "Belly Button",
        "duration": 15,
        "metahash": "1e20c4933dc8c03ea58568159a1cbfb04132c7db93b6b4cd025ffd4db37f52a4756f",
    }


def test_code_meta_video(mp4_file):
    assert idk.code_meta(mp4_file).dict() == {
        "iscc": "ISCC:AAAV6UK6BSXJ3I4G",
        "name": "Kali by Anokato - Spiral Sessions 2019",
        "metahash": "1e2096c0a53475a186ce37622aba7ba70651fc62cc8150f59eee6d17dc16d9bfbf25",
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
        "thumbnail": "data:image/webp;base64,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",
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
                "features": ["eGluK69boGk"],
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
        "thumbnail": "data:image/webp;base64,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",
        "width": 200,
    }


def test_code_video(mp4_file):
    assert idk.code_video(mp4_file).dict() == {
        "iscc": "ISCC:EMAV4DUD6QORW4X4",
        "name": "Kali by Anokato - Spiral Sessions 2019",
        "thumbnail": "data:image/webp;base64,UklGRkAFAABXRUJQVlA4IDQFAABQHACdASqAAGkAPrVUoU0nJL+iJds7o/AWiUAaVUmMC9Ymbvi4gI54bTdt50rwr7N+M3nP42/ab9zzG+k74b8n/VrvT9OHkr3QnKPB0+k/qr4qX8d6D/UjzQ/9N6a94N4t7AH8n/u3/R9lT+k8bP0p7Af66dcEw8O/Fjh0V9q/EzGIXOPxxGpc24WPN9p12h+zeDRpntIPLKARwz62m3BPGyFS9rzZiv3VJlg+hNKMMfZMQJzHYwM5pXOu/B8cvvwU0x4TrPQT/1NWb1QiI/XoZOGjVrAntgus6zRf5zFWbUxamLYiInReOWnQAP750EAB6/Gz7ppI6A3w/zt8U/tR4HwZILZiEJ39oTo6Jf1u3N4w7w0ALWz10zrZ8GVMOcoN7ib8ZG9jZz1xUfcW9Sdg0+9vgh5GLQpOT77rQTmy2vkPAmUpMeQOnCAYqmD8In78khGhd2PPfNzF5wjbMmcxmZr8pk0Tzza+jvY6twcoqfijYdYqRMT6BRQl95E1TQJ2vBWwn/5P406F/viJYID3/5Dl3LJlsmMlCDoIcd8zEtx+XLqcpUaER8pnGFbViIzy/0X3LvUkP9xlJzidkB3CgqYf26aIdunTUCYRLfeSpj2yptiOXx0YmRzx5XxrPm3i7GO2smpd6/o9ZIX9Q3vG20223jlv2Qrl2PToH2G91tWwDBpFLiyX+ojOGEyAtJ+PIxKoIxthBeved8lNoDHtsI2dur5AhYy0TVIwP0e6fQ0lsiHaEdU8AvOFGw5f/WaKrif6HjVbFKFQgEyBbFUQM8Xrykx3X8cKCq0EPcjj2ggd++n10yVCX4GSdB/Trerpf69HVhpJtMZLynD1z3cf9VI28q+1/LtCt8W7yI7GTekUoZaDEjALNUNT8ry/l9egi6aK59BAYWqvDgT8Vcu7hOiFL/qJBepaPtIUQkin19qvzT+9T0d8SGoG0binZs1UbMxY1phQeT3U16T17OxvcmhVnOV0C92EginYKqZw5n/xat/JbmptnAZP19BGkcOqnRCxVeJgwkxRB9vzu1xLM1i3Dt+WKXyv50lK4ykfU2srsOJHpSLgMz75gbyhEitaPiW49IooZ7Ae61bI6JMoI0N7kBDpFs8jOGXtczQBSAEtVe++l89JefzWcS2EH9Lmyk3+q7O0yHz2eE3KcImzXnN8AL/kcB0H28Y2q7WTRjGPg7qIzeg5rsuOBsSMstmMfGM1YDWb9k55rWvedKYcrQc4Tyc4uxLXOoZzfPfXVHO6sFJBw2DGX3n6sb8fegUVN+uxLKJnO4fkvw3aD6aamRI2lL1m3Z6YeRbIRkVAUbxu7QkFcfQ/NmygSImoYv96fjbxvoQLSMdaSj5ZCYYgx/J8n/XyeRaCsWAOeUqsx93z+Fq0JPrnOxm9ypga1WYQhn8RYnGjcd+y6uHoq7VAzXunweVYJGYMD5IDBZtaYCywWZHM2z5FtkzAlomZR173ct/Ls+p036ukw/nMbCKeHnkJ884g1xNf6Flzc7LRTA0H6Ttrz3rukIxtReTvlQ1FuI9QCxk3tVP9MzNrHhtwq85YHYLcgBopKZqMJxkCm62YZ+ckmErtGImje7dBmxlAZe290TV0R2vYx51znfnph4aLw6OiksjFM//JnYh/JEMYlTjl/v4LCa8qFgHQ/yPJql1BtdwmM9g3NkoL50nf/cOlQmSwljeE33QqAp0NwgkAlo7c3/LEib8gvzr+CHETvA4pAL1yMJfLDfxlG5U/+AeRF6lDsnZfKTDeUeZwAAAAAAA=",
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
    assert idk.code_iscc(new_file).dict() == {
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
        "thumbnail": "data:image/webp;base64,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",
        "width": 200,
    }
