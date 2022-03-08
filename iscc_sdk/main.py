"""SDK main top-level functions."""
from os.path import basename

import iscc_core as ic
from PIL import Image
import iscc_sdk as idk


__all__ = [
    "code_meta",
    "code_image",
    "code_data",
    "code_instance",
]


def code_meta(fp):
    # type (str) -> idk.IsccMeta
    """Generate Meta-Code from digital asset."""

    with open(fp, "rb") as infile:
        data = infile.read(4096)

    mediatype = idk.mime_guess(data, file_name=basename(fp))
    mode = idk.mime_to_mode(mediatype)

    if mode != "image":
        raise ValueError("Unsupported mediatype: {}".format(mediatype))
    meta = idk.image_meta_extract(fp)
    if not meta.get("name"):
        meta["name"] = idk.text_name_from_uri(fp)

    metacode = ic.gen_meta_code_v0(
        name=meta.get("name"),
        description=meta.get("description"),
        meta=meta.get("meta"),
        bits=idk.sdk_opts.meta_bits,
    )

    meta.update(metacode)

    return idk.IsccMeta(**meta)


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
    code_obj = ic.gen_image_code_v0(pixels, bits=idk.sdk_opts.image_bits)
    meta_obj = idk.IsccMeta(iscc=code_obj["iscc"], thumbnail=thumnnail_durl, **meta)
    return meta_obj


def code_data(fp):
    # type: (str) -> idk.IsccMeta
    """Create ISCC Data-Code.

    The Data-Code is a similarity preserving hash of the input data.

    :param str fp: Filepath used for Data-Code creation.
    :return: IsccMeta object with Data-Code
    :rtype: IsccMeta
    """

    with open(fp, "rb") as stream:
        result = ic.gen_data_code_v0(stream, bits=idk.sdk_opts.data_bits)

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
