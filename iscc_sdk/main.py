"""*SDK main top-level functions*."""
from os.path import basename

from PIL import Image
import iscc_core as ic
import iscc_sdk as idk


__all__ = [
    "code_iscc",
    "code_meta",
    "code_content",
    "code_text",
    "code_image",
    "code_audio",
    "code_video",
    "code_data",
    "code_instance",
]


def code_iscc(fp):
    # type: (str) -> idk.IsccMeta
    """
    Generate ISCC-CODE.

    The ISCC-CODE is a composite of Meta, Content, Data and Instance Codes.

    :param str fp: Filepath used for ISCC-CODE creation.
    :return: ISCC metadata including ISCC-CODE and merged metadata from ISCC-UNITs.
    :rtype: IsccMeta
    """

    # Generate ISCC-UNITs
    instance = code_instance(fp)
    data = code_data(fp)
    content = code_content(fp)
    meta = code_meta(fp)

    # Compose ISCC-CODE
    iscc_code = ic.gen_iscc_code_v0([meta.iscc, content.iscc, data.iscc, instance.iscc])

    # Merge ISCC Metadata
    iscc_meta = dict(filename=basename(fp))
    iscc_meta.update(instance.dict())
    iscc_meta.update(data.dict())
    iscc_meta.update(content.dict())
    iscc_meta.update(meta.dict())
    iscc_meta.update(iscc_code)
    return idk.IsccMeta.parse_obj(iscc_meta)


def code_meta(fp):
    # type: (str) -> idk.IsccMeta
    """
    Generate Meta-Code from digital asset.

    :param str fp: Filepath used for Meta-Code creation.
    :return: ISCC metadata including Meta-Code and extracted metadata fields.
    :rtype: IsccMeta
    """

    meta = idk.extract_metadata(fp).dict()

    if not meta.get("name"):
        meta["name"] = idk.text_name_from_uri(fp)

    metacode = ic.gen_meta_code_v0(
        name=meta.get("name"),
        description=meta.get("description"),
        meta=meta.get("meta"),
        bits=idk.sdk_opts.meta_bits,
    )

    meta.update(metacode)
    return idk.IsccMeta.parse_obj(meta)


def code_content(fp):
    # type: (str) -> idk.IsccMeta
    """
    Detect mediatype and create corresponding Content-Code.

    :param str fp: Filepath
    :return: Content-Code wrapped in ISCC metadata.
    :rtype: IsccMeta
    """

    schema_org_map = {
        "text": "TextDigitalDocument",
        "image": "ImageObject",
        "audio": "AudioObject",
        "video": "VideoObject",
    }

    mediatype, mode = idk.mediatype_and_mode(fp)

    if mode == "image":
        cc = code_image(fp)
    elif mode == "audio":
        cc = code_audio(fp)
    elif mode == "video":
        cc = code_video(fp)
    elif mode == "text":
        cc = code_text(fp)
    else:  # pragma nocover
        raise idk.IsccUnsupportedMediatype(mediatype)

    cc.mediatype = mediatype
    cc.mode = mode
    cc.type_ = schema_org_map.get(mode)

    return cc


def code_text(fp):
    """
    Generate Content-Code Text.

    :param str fp: Filepath used for Text-Code creation.
    :return: ISCC metadata including Text-Code.
    :rtype: IsccMeta
    """
    meta = idk.text_meta_extract(fp)
    text = idk.text_extract(fp)
    code = ic.gen_text_code_v0(text, bits=idk.sdk_opts.text_bits)
    meta.update(code)
    return idk.IsccMeta.parse_obj(meta)


def code_image(fp):
    # type: (str) -> idk.IsccMeta
    """
    Generate Content-Code Image.

    :param str fp: Filepath used for Image-Code creation.
    :return: ISCC metadata including Image-Code.
    :rtype: IsccMeta
    """
    meta = idk.image_meta_extract(fp)

    thumbnail_img = idk.image_thumbnail(fp)
    thumnnail_durl = idk.image_to_data_url(thumbnail_img)
    meta["thumbnail"] = thumnnail_durl

    pixels = idk.image_normalize(Image.open(fp))
    code_obj = ic.gen_image_code_v0(pixels, bits=idk.sdk_opts.image_bits)
    meta.update(code_obj)

    return idk.IsccMeta.parse_obj(meta)


def code_audio(fp):
    # type: (str) -> idk.IsccMeta
    """
    Generate Content-Code Audio.

    :param str fp: Filepath used for Audio-Code creation.
    :return: ISCC metadata including Audio-Code.
    :rtype: IsccMeta
    """
    meta = idk.audio_meta_extract(fp)
    features = idk.audio_features_extract(fp)
    code_obj = ic.gen_audio_code_v0(features["fingerprint"], bits=idk.sdk_opts.audio_bits)
    meta.update(code_obj)

    return idk.IsccMeta.parse_obj(meta)


def code_video(fp):
    # type: (str) -> idk.IsccMeta
    """
    Generate Content-Code Video.

    :param str fp: Filepath used for Video-Code creation.
    :return: ISCC metadata including Image-Code.
    :rtype: IsccMeta
    """
    meta = idk.video_meta_extract(fp)
    features = idk.video_features_extract(fp)
    code_obj = ic.gen_video_code_v0(features, bits=idk.sdk_opts.video_bits)
    meta.update(code_obj)
    thumbnail_image = idk.video_thumbnail(fp)
    thumbnail_durl = idk.image_to_data_url(thumbnail_image)
    meta["thumbnail"] = thumbnail_durl
    return idk.IsccMeta.parse_obj(meta)


def code_data(fp):
    # type: (str) -> idk.IsccMeta
    """
    Create ISCC Data-Code.

    The Data-Code is a similarity preserving hash of the input data.

    :param str fp: Filepath used for Data-Code creation.
    :return: ISCC metadata including Data-Code.
    :rtype: IsccMeta
    """

    with open(fp, "rb") as stream:
        meta = ic.gen_data_code_v0(stream, bits=idk.sdk_opts.data_bits)

    return idk.IsccMeta.parse_obj(meta)


def code_instance(fp):
    # type: (str) -> idk.IsccMeta
    """
    Create ISCC Instance-Code.

    The Instance-Code is prefix of a cryptographic hash (blake3) of the input data.
    It´s purpose is to serve as a checksum that detects even minimal changes
    to the data of the referenced media asset. For cryptographicaly secure integrity
    checking a full 256-bit multihash is provided with the `datahash` field.

    :param str fp: Filepath used for Instance-Code creation.
    :return: ISCC metadata including Instance-Code, datahash and filesize.
    :rtype: IsccMeta
    """
    with open(fp, "rb") as stream:
        meta = ic.gen_instance_code_v0(stream, bits=idk.sdk_opts.instance_bits)

    return idk.IsccMeta.parse_obj(meta)
