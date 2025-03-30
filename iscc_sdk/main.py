"""*SDK main top-level functions*."""

from typing import Any

from loguru import logger as log
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
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


def code_iscc(fp, **options):
    # type: (str|Path, Any) -> idk.IsccMeta
    """
    Generate a complete ISCC-CODE for the given file.

    This function creates a full ISCC-CODE by combining Meta, Content, Data, and Instance Codes.
    It automatically detects the media type and processes the file accordingly.

    The function performs the following steps:
    1. Reads the file and determines its MIME type.
    2. Generates Instance and Data Codes for all file types.
    3. For supported media types, generates Content and Meta Codes.
    4. Combines all generated codes into a single ISCC-CODE.
    5. Merges metadata from all ISCC units.

    Note:

    - This function uses multithreading to improve performance.
    - The behavior can be customized through the `sdk_opts` settings. For example, setting
      `fallback` to True will allow processing of unsupported media types in a
      fallback mode instead of raising an exception.

    :param fp: str or Path object representing the filepath of the file to process.
    :param options: Custom processing options for overriding global options
    :return: IsccMeta object with complete ISCC-CODE and merged metadata from all ISCC-UNITs.
    :raises idk.IsccUnsupportedMediatype:
        If the media type is not supported. By default, the function will raise this exception for
        unsupported media types, as sdk_opts.fallback is False by default.
    """
    fp = Path(fp)
    opts = idk.sdk_opts.override(options)
    iscc_meta = dict(filename=fp.name)
    iscc_units = []

    with open(fp, "rb") as infile:
        data = infile.read(4096)

    mime = idk.mediatype_guess(data, file_name=fp.name)
    iscc_meta["mediatype"] = mime

    with ThreadPoolExecutor() as executor:
        # Always process instance and data
        instance_future = executor.submit(code_instance, fp)
        data_future = executor.submit(code_data, fp)
        try:
            mode = idk.mediatype_to_mode(mime)
            log.debug(f"Processing {fp.name} - media type: {mime} - processing mode: {mode}")

        except idk.IsccUnsupportedMediatype:
            if not opts.fallback:
                raise
            log.warning(f"Processing {fp.name} - media type: {mime} - processing mode: sum")
        else:
            # Process content and meta for supported media types
            content_future = executor.submit(code_content, fp, False, None)
            meta_future = executor.submit(code_meta, fp)

            content = content_future.result()
            meta = meta_future.result()
            iscc_units.extend([meta.iscc, content.iscc])
            iscc_meta.update(content.dict())
            iscc_meta.update(meta.dict())
        finally:
            # Wait for instance and data to complete
            instance = instance_future.result()
            data = data_future.result()
            iscc_units.extend([data.iscc, instance.iscc])
            iscc_meta.update(instance.dict())
            iscc_meta.update(data.dict())

    # Compose ISCC-CODE
    iscc_code = ic.gen_iscc_code_v0(iscc_units)
    iscc_meta.update(iscc_code)
    iscc_meta["generator"] = f"iscc-sdk - v{idk.__version__}"

    return idk.IsccMeta.construct(**iscc_meta)


def code_meta(fp):
    # type: (str|Path) -> idk.IsccMeta
    """
    Generate Meta-Code from digital asset.

    :param fp: Filepath used for Meta-Code creation.
    :return: ISCC metadata including Meta-Code and extracted metadata fields.
    """
    fp = Path(fp)

    meta = idk.extract_metadata(fp).dict()

    # Pre-Check if we have a name after normalization, else use filename.
    name = meta.get("name")
    name = "" if name is None else name
    name = ic.text_clean(name)
    name = ic.text_remove_newlines(name)
    name = ic.text_trim(name, ic.core_opts.meta_trim_name)
    if not name:
        meta["name"] = idk.text_name_from_uri(fp)
        log.debug(f"Acquired Meta-Code `name` from filename: {meta['name']}")

    metacode = ic.gen_meta_code_v0(
        name=meta.get("name"),
        description=meta.get("description"),
        meta=meta.get("meta"),
        bits=idk.core_opts.meta_bits,
    )

    meta.update(metacode)
    return idk.IsccMeta.construct(**meta)


def code_content(fp, extract_meta=None, create_thumb=None):
    # type: (str|Path, bool|None, bool|None) -> idk.IsccMeta
    """
    Detect mediatype and create corresponding Content-Code.

    :param fp: Filepath
    :param extract_meta: Whether to extract metadata.
    :param create_thumb: Whether to create a thumbnail.
    :return: Content-Code wrapped in ISCC metadata.
    """
    fp = Path(fp)
    schema_org_map = {
        "text": "TextDigitalDocument",
        "image": "ImageObject",
        "audio": "AudioObject",
        "video": "VideoObject",
    }

    mediatype, mode = idk.mediatype_and_mode(fp)

    if mode == "image":
        cc = code_image(fp, extract_meta, create_thumb)
    elif mode == "audio":
        cc = code_audio(fp, extract_meta, create_thumb)
    elif mode == "video":
        cc = code_video(fp, extract_meta, create_thumb)
    elif mode == "text":
        cc = code_text(fp, extract_meta, create_thumb)
    else:  # pragma nocover
        raise idk.IsccUnsupportedMediatype(mediatype)

    cc.mediatype = mediatype
    cc.mode = mode
    cc.type_ = schema_org_map.get(mode)

    return cc


def code_text(fp, extract_meta=None, create_thumb=None):
    # type: (str|Path, bool|None, bool|None) -> idk.IsccMeta
    """
    Generate Content-Code Text.

    :param fp: Filepath used for Text-Code creation.
    :param extract_meta: Whether to extract metadata.
    :param create_thumb: Whether to create a thumbnail.
    :return: ISCC metadata including Text-Code.
    """
    fp = Path(fp)
    meta = dict()

    if extract_meta is None:
        extract_meta = idk.sdk_opts.extract_metadata
    if create_thumb is None:
        create_thumb = idk.sdk_opts.create_thumbnail

    if extract_meta:
        meta = idk.text_meta_extract(fp)

    if create_thumb:
        thumbnail_img = idk.text_thumbnail(fp)
        if thumbnail_img:
            thumbnail_durl = idk.image_to_data_url(thumbnail_img)
            meta["thumbnail"] = thumbnail_durl

    text = idk.text_extract(fp)
    code = ic.gen_text_code_v0(text, bits=idk.core_opts.text_bits)
    meta.update(code)
    if idk.sdk_opts.granular:
        features = idk.text_features(text)
        meta["features"] = [features]
    return idk.IsccMeta.construct(**meta)


def code_image(fp, extract_meta=None, create_thumb=None):
    # type: (str|Path, bool|None, bool|None) -> idk.IsccMeta
    """
    Generate Content-Code Image.

    :param fp: Filepath used for Image-Code creation.
    :param extract_meta: Whether to extract metadata.
    :param create_thumb: Whether to create a thumbnail.
    :return: ISCC metadata including Image-Code.
    """
    fp = Path(fp)
    meta = dict()

    if extract_meta is None:
        extract_meta = idk.sdk_opts.extract_metadata
    if create_thumb is None:
        create_thumb = idk.sdk_opts.create_thumbnail

    if extract_meta:
        meta = idk.image_meta_extract(fp)
    if create_thumb:
        thumbnail_img = idk.image_thumbnail(fp)
        thumbnail_durl = idk.image_to_data_url(thumbnail_img)
        meta["thumbnail"] = thumbnail_durl

    pixels = idk.image_normalize(Image.open(fp))
    code_obj = ic.gen_image_code_v0(pixels, bits=idk.core_opts.image_bits)
    meta.update(code_obj)

    return idk.IsccMeta.construct(**meta)


def code_audio(fp, extract_meta=None, create_thumb=None):
    # type: (str|Path, bool|None, bool|None) -> idk.IsccMeta
    """
    Generate Content-Code Audio.

    :param fp: Filepath used for Audio-Code creation.
    :param extract_meta: Whether to extract metadata.
    :param create_thumb: Whether to create a thumbnail.
    :return: ISCC metadata including Audio-Code.
    """
    fp = Path(fp)
    meta = dict()

    if extract_meta is None:
        extract_meta = idk.sdk_opts.extract_metadata
    if create_thumb is None:
        create_thumb = idk.sdk_opts.create_thumbnail

    if extract_meta:
        meta = idk.audio_meta_extract(fp)
    if create_thumb:
        thumbnail_img = idk.audio_thumbnail(fp)
        if thumbnail_img:
            thumbnail_durl = idk.image_to_data_url(thumbnail_img)
            meta["thumbnail"] = thumbnail_durl

    features = idk.audio_features_extract(fp)
    code_obj = ic.gen_audio_code_v0(features["fingerprint"], bits=idk.core_opts.audio_bits)
    meta.update(code_obj)

    return idk.IsccMeta.construct(**meta)


def code_video(fp, extract_meta=None, create_thumb=None):
    # type: (str|Path) -> idk.IsccMeta
    """
    Generate Content-Code Video.

    :param fp: Filepath used for Video-Code creation.
    :param extract_meta: Whether to extract metadata.
    :param create_thumb: Whether to create a thumbnail.
    :return: ISCC metadata including Image-Code.
    """
    fp = Path(fp)
    meta = dict()

    if extract_meta is None:
        extract_meta = idk.sdk_opts.extract_metadata
    if create_thumb is None:
        create_thumb = idk.sdk_opts.create_thumbnail

    if extract_meta:
        meta = idk.video_meta_extract(fp)

    if create_thumb:
        thumbnail_image = idk.video_thumbnail(fp)
        if thumbnail_image is not None:
            thumbnail_durl = idk.image_to_data_url(thumbnail_image)
            meta["thumbnail"] = thumbnail_durl

    sig, scenes = None, []
    if idk.sdk_opts.granular:
        sig, scenes = idk.video_mp7sig_extract_scenes(fp)
    else:
        sig = idk.video_mp7sig_extract(fp)

    if idk.sdk_opts.video_store_mp7sig:
        outp = fp.with_suffix(".iscc.mp7sig")
        with open(outp, "wb") as outf:
            outf.write(sig)

    frames = idk.read_mp7_signature(sig)
    features = [tuple(frame.vector.tolist()) for frame in frames]

    code_obj = ic.gen_video_code_v0(features, bits=idk.core_opts.video_bits)
    meta.update(code_obj)

    if idk.sdk_opts.granular:
        granular = idk.video_compute_granular(frames, scenes)
        meta["features"] = granular

    return idk.IsccMeta.construct(**meta)


def code_data(fp):
    # type: (str|Path) -> idk.IsccMeta
    """
    Create ISCC Data-Code.

    The Data-Code is a similarity preserving hash of the input data.

    :param fp: Filepath used for Data-Code creation.
    :return: ISCC metadata including Data-Code.
    """
    fp = Path(fp)
    with open(fp, "rb") as stream:
        meta = ic.gen_data_code_v0(stream, bits=idk.core_opts.data_bits)

    return idk.IsccMeta.construct(**meta)


def code_instance(fp):
    # type: (str|Path) -> idk.IsccMeta
    """
    Create ISCC Instance-Code.

    The Instance-Code is prefix of a cryptographic hash (blake3) of the input data.
    It´s purpose is to serve as a checksum that detects even minimal changes
    to the data of the referenced media asset. For cryptographicaly secure integrity
    checking a full 256-bit multihash is provided with the `datahash` field.

    :param fp: Filepath used for Instance-Code creation.
    :return: ISCC metadata including Instance-Code, datahash and filesize.
    """
    fp = Path(fp)
    with open(fp, "rb") as stream:
        meta = ic.gen_instance_code_v0(stream, bits=idk.core_opts.instance_bits)

    return idk.IsccMeta.construct(**meta)
