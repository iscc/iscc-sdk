"""SDK main top-level functions."""
import iscc_core as ic
from PIL import Image
import iscc_sdk as idk


__all__ = [
    "code_image",
    "code_data",
    "code_instance",
]


def code_image(fp):
    # type: (str) -> idk.IsccMeta
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
    meta_obj = idk.IsccMeta.construct(iscc=code_obj["iscc"], thumbnail=thumnnail_durl, **meta)
    return meta_obj


def code_data(fp):
    # type: (str) -> idk.IsccMeta
    """Create ISCC Data-Code.

    The Data-Code is a similarity preserving hash of the input data.

    :param str fp: Filepath used for Data-Code creation.
    :return: IsccMeta object with Data-Code
    :rtype: idk.IsccMeta
    """

    with open(fp, "rb") as stream:
        result = ic.gen_data_code(stream)

    return idk.IsccMeta(**result)


def code_instance(fp):
    # type: (str) -> idk.IsccMeta
    """Create ISCC Instance-Code.

    The Instance-Code is prefix of a cryptographic hash (blake3) of the input data.
    It´s purpose is to serve as a checksum that detects even minimal changes
    to the data of the referenced media asset. For cryptographicaly secure integrity
    checking a full 256-bit multihash is provided with the `datahash` field.

    :param str fp: Filepath to file used for Instance-Code creation.
    :return: IsccMeta object with Instance-Code, datahash and filesize
    :rtype: IsccMeta
    """
    with open(fp, "rb") as stream:
        result = ic.gen_instance_code_v0(stream, bits=idk.sdk_opts.instance_bits)
    return idk.IsccMeta(**result)
