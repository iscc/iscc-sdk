"""SDK main top-level functions."""
import iscc_core as ic
from PIL import Image
import iscc_sdk as idk
from iscc_schema import IsccMeta


__all__ = [
    "code_image",
]


def code_image(fp):
    # type: (str) -> IsccMeta
    """Generate Content-Code Image.

    :param str fp: Filepath to image file
    :return: ISCC Metadata
    :rtype: IsccMeta
    """
    meta = idk.image_meta_extract(fp)
    thumbnail_img = idk.image_thumbnail(fp)
    thumnnail_durl = idk.image_to_data_url(thumbnail_img)
    pixels = idk.image_normalize(Image.open(fp))
    code_obj = ic.gen_image_code_v0(pixels)
    meta_obj = IsccMeta.construct(iscc=code_obj["iscc"], thumbnail=thumnnail_durl, **meta)
    return meta_obj
