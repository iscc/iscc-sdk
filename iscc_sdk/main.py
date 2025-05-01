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
    "code_text_semantic",
    "code_image",
    "code_image_semantic",
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
    :key fallback: Process unsupported media types. Default: False
    :key add_units: Include ISCC-UNITS in metadata. Default: False
    :key create_meta: Create Meta-Code unit from embedded metadata. Default: True
    :key wide: Enable wide mode for ISCC-SUM with Data & Instance codes only. Default: False
    :key experimental: Enable experimental semantic codes. Default: False
    :return: IsccMeta object with complete ISCC-CODE and merged metadata from all ISCC-UNITs.
    :raises idk.IsccUnsupportedMediatype:
        If the media type is not supported. By default, the function will raise this exception for
        unsupported media types, as sdk_opts.fallback is False by default.
    """
    fp = Path(fp)
    opts = idk.sdk_opts.override(options)
    iscc_meta = dict(filename=fp.name)

    # Track list properties for custom merging
    iscc_units = []
    iscc_features = []

    with open(fp, "rb") as infile:
        data = infile.read(4096)

    mime = idk.mediatype_guess(data, file_name=fp.name)
    iscc_meta["mediatype"] = mime

    with ThreadPoolExecutor() as executor:
        # Always process instance and data
        instance_future = executor.submit(code_instance, fp, **options)
        data_future = executor.submit(code_data, fp, **options)
        try:
            mode = idk.mediatype_to_mode(mime)
            log.debug(f"Processing {fp.name} - media type: {mime} - processing mode: {mode}")

        except idk.IsccUnsupportedMediatype:
            if not opts.fallback:
                raise
            log.warning(f"Processing {fp.name} - media type: {mime} - processing mode: sum")
        else:
            # Process content and meta for supported media types
            content_future = executor.submit(code_content, fp, **options)
            if opts.create_meta:
                meta_future = executor.submit(code_meta, fp, **options)
                meta = meta_future.result()
                iscc_units.append(meta.iscc)

            # Optional semantic codes
            if mode == "image" and idk.is_installed("iscc_sci") and opts.experimental:
                content_semantic_future = executor.submit(code_image_semantic, fp)
            elif mode == "text" and idk.is_installed("iscc_sct") and opts.experimental:
                content_semantic_future = executor.submit(code_text_semantic, fp)
            else:
                content_semantic_future = None

            if content_semantic_future:
                content_semantic = content_semantic_future.result()
                iscc_units.append(content_semantic.iscc)
                if content_semantic.features:
                    iscc_features.append(content_semantic.features[0])
                iscc_meta.update(content_semantic.dict(exclude={"features"}))

            content = content_future.result()
            iscc_units.append(content.iscc)
            if content.features:
                iscc_features.append(content.features[0])
            iscc_meta.update(content.dict(exclude={"features"}))
            if opts.create_meta:
                iscc_meta.update(meta.dict())

        finally:
            # Wait for instance and data to complete
            instance = instance_future.result()
            data = data_future.result()
            iscc_units.extend([data.iscc, instance.iscc])
            iscc_meta.update(instance.dict())
            iscc_meta.update(data.dict())

    if opts.add_units:
        iscc_meta["units"] = iscc_units
    if iscc_features:
        iscc_meta["features"] = iscc_features

    # Compose ISCC-CODE
    iscc_code = ic.gen_iscc_code_v0(iscc_units, wide=opts.wide)
    iscc_meta.update(iscc_code)
    iscc_meta["generator"] = f"iscc-sdk - v{idk.__version__}"

    result = idk.IsccMeta.construct(**iscc_meta)

    if opts.process_container:
        parts = idk.process_container(fp, **options)
        if parts:
            result.parts = parts

    return result


def code_meta(fp, **options):
    # type: (str|Path, Any) -> idk.IsccMeta
    """
    Generate Meta-Code from digital asset.

    Creates an ISCC Meta-Code based on normalized metadata extracted from the file.
    If no name is found in metadata, the filename will be used instead.

    :param fp: Filepath used for Meta-Code creation.
    :key bits: Bit-length of the generated Meta-Code UNIT. Default: 64
    :return: ISCC metadata including Meta-Code and extracted metadata fields.
    """
    fp = Path(fp)
    opts = idk.sdk_opts.override(options)

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
        bits=opts.bits,
    )

    meta.update(metacode)
    return idk.IsccMeta.construct(**meta)


def code_content(fp, **options):
    # type: (str|Path, Any) -> idk.IsccMeta
    """
    Detect mediatype and create corresponding Content-Code.

    Analyzes the file to determine its media type and routes the processing to the
    appropriate specialized function (code_text, code_image, code_audio, or code_video).

    :param fp: Filepath
    :key extract_meta: Whether to extract metadata. Default: True
    :key create_thumb: Whether to create a thumbnail. Default: True
    :return: Content-Code wrapped in ISCC metadata.
    :raises idk.IsccUnsupportedMediatype: If the media type is not supported.
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
        cc = code_image(fp, **options)
    elif mode == "audio":
        cc = code_audio(fp, **options)
    elif mode == "video":
        cc = code_video(fp, **options)
    elif mode == "text":
        cc = code_text(fp, **options)
    else:  # pragma nocover
        raise idk.IsccUnsupportedMediatype(mediatype)

    cc.mediatype = mediatype
    cc.mode = mode
    cc.type_ = schema_org_map.get(mode)

    return cc


def code_text(fp, **options):
    # type: (str|Path, Any) -> idk.IsccMeta
    """
    Generate Content-Code Text.

    Creates a Text-Code by extracting and processing text content from document files.
    Can optionally extract metadata and create a thumbnail representation of the text.

    :param fp: Filepath used for Text-Code creation.
    :key extract_meta: Whether to extract metadata. Default: True
    :key create_thumb: Whether to create a thumbnail. Default: True
    :key bits: Bit-length of the generated Text-Code UNIT. Default: 64
    :key granular: Whether to generate additional granular fingerprints. Default: False
    :return: ISCC metadata including Text-Code.
    """
    fp = Path(fp)
    opts = idk.sdk_opts.override(options)
    meta = dict()

    if opts.extract_meta:
        meta = idk.text_meta_extract(fp)

    if opts.create_thumb:
        thumbnail_img = idk.text_thumbnail(fp)
        if thumbnail_img:
            thumbnail_durl = idk.image_to_data_url(thumbnail_img)
            meta["thumbnail"] = thumbnail_durl

    text = idk.text_extract(fp)
    text = ic.text_clean(text)
    code = ic.gen_text_code_v0(text, bits=opts.bits)
    meta.update(code)
    if opts.granular:
        features = idk.text_features(text)
        meta["features"] = [features]
    if opts.text_keep:
        meta["text"] = text
    return idk.IsccMeta.construct(**meta)


def code_text_semantic(fp, **options):  # pragma: no cover
    # type: (str|Path, Any) -> idk.IsccMeta
    """
    Generate Semantic-Code Text. (Requires iscc-sct to be installed)
    :param fp: Filepath used for semantic Text-Code creation.
    :raises idk.EnvironmentError: If iscc-sct is not installed.
    """
    if not idk.is_installed("iscc_sct"):
        raise idk.EnvironmentError(
            "Semantic-Code Text requires `iscc-sct` package to be installed."
        )
    import iscc_sct

    fp = Path(fp)
    opts = iscc_sct.sct_opts.override(options)
    text = idk.text_extract(fp)
    text = ic.text_clean(text)
    result = iscc_sct.gen_text_code_semantic(text, **opts.model_dump())
    return idk.IsccMeta.construct(**result)


def code_image(fp, **options):
    # type: (str|Path, Any) -> idk.IsccMeta
    """
    Generate Content-Code Image.

    Creates an Image-Code by normalizing and processing the visual content of image files.
    The image is normalized according to SDK options (transparency handling, border trimming, ...).

    :param fp: Filepath used for Image-Code creation.
    :key extract_meta: Whether to extract metadata. Default: True
    :key create_thumb: Whether to create a thumbnail. Default: True
    :key bits: Bit-length of the generated Image-Code UNIT. Default: 64
    :return: ISCC metadata including Image-Code.
    """
    fp = Path(fp)
    opts = idk.sdk_opts.override(options)
    meta = dict()

    if opts.extract_meta:
        meta = idk.image_meta_extract(fp)
    if opts.create_thumb:
        thumbnail_img = idk.image_thumbnail(fp)
        thumbnail_durl = idk.image_to_data_url(thumbnail_img)
        meta["thumbnail"] = thumbnail_durl

    pixels = idk.image_normalize(Image.open(fp))
    code_obj = ic.gen_image_code_v0(pixels, bits=opts.bits)
    meta.update(code_obj)

    return idk.IsccMeta.construct(**meta)


def code_image_semantic(fp, **options):  # pragma: no cover
    # type: (str|Path, Any) -> idk.IsccMeta
    """
    Generate Semantic-Code Image. (Requires iscc-sci to be installed)
    :param fp: Filepath used for semantic Image-Code creation.
    :raises idk.EnvironmentError: If iscc-sci is not installed.
    """
    if not idk.is_installed("iscc_sci"):
        raise idk.EnvironmentError(
            "Semantic-Code Image requires `iscc-sci` package to be installed."
        )
    import iscc_sci

    fp = Path(fp)
    opts = iscc_sci.sci_opts.override(options)
    meta = iscc_sci.code_image_semantic(fp, **opts.model_dump())
    return idk.IsccMeta.construct(**meta)


def code_audio(fp, **options):
    # type: (str|Path, Any) -> idk.IsccMeta
    """
    Generate Content-Code Audio.

    Creates an Audio-Code by extracting acoustic fingerprints from audio files.
    Uses chromaprint/fpcalc to generate audio features for similarity matching.

    :param fp: Filepath used for Audio-Code creation.
    :key extract_meta: Whether to extract metadata. Default: True
    :key create_thumb: Whether to create a thumbnail. Default: True
    :key bits: Bit-length of the generated Audio-Code UNIT. Default: 64
    :return: ISCC metadata including Audio-Code.
    """
    fp = Path(fp)
    opts = idk.sdk_opts.override(options)
    meta = dict()

    if opts.extract_meta:
        meta = idk.audio_meta_extract(fp)
    if opts.create_thumb:
        thumbnail_img = idk.audio_thumbnail(fp)
        if thumbnail_img:
            thumbnail_durl = idk.image_to_data_url(thumbnail_img)
            meta["thumbnail"] = thumbnail_durl

    features = idk.audio_features_extract(fp)
    code_obj = ic.gen_audio_code_v0(features["fingerprint"], bits=opts.bits)
    meta.update(code_obj)

    return idk.IsccMeta.construct(**meta)


def code_video(fp, **options):
    # type: (str|Path, Any) -> idk.IsccMeta
    """
    Generate Content-Code Video.

    Creates a Video-Code by extracting and processing visual features from video frames.
    Uses MPEG-7 signature tools to extract frame-based features and optionally detect scene changes.

    :param fp: Filepath used for Video-Code creation.
    :key extract_meta: Whether to extract metadata. Default: True
    :key create_thumb: Whether to create a thumbnail. Default: True
    :key granular: Generate additional fingerprints based on scenes. Default: False
    :key video_store_mp7sig: Whether to store extracted MP7 Video signature file. Default: False
    :key bits: Bit-length of the generated Video-Code UNIT. Default: 64
    :return: ISCC metadata including Video-Code.
    """
    fp = Path(fp)
    opts = idk.sdk_opts.override(options)
    meta = dict()

    if opts.extract_meta:
        meta = idk.video_meta_extract(fp)

    if opts.create_thumb:
        thumbnail_image = idk.video_thumbnail(fp)
        if thumbnail_image is not None:
            thumbnail_durl = idk.image_to_data_url(thumbnail_image)
            meta["thumbnail"] = thumbnail_durl

    sig, scenes = None, []
    if opts.granular:
        sig, scenes = idk.video_mp7sig_extract_scenes(fp)
    else:
        sig = idk.video_mp7sig_extract(fp)

    if opts.video_store_mp7sig:
        outp = fp.with_suffix(".iscc.mp7sig")
        with open(outp, "wb") as outf:
            outf.write(sig)

    frames = idk.read_mp7_signature(sig)
    features = [tuple(frame.vector.tolist()) for frame in frames]

    code_obj = ic.gen_video_code_v0(features, bits=opts.bits)
    meta.update(code_obj)

    if opts.granular:
        granular = idk.video_compute_granular(frames, scenes)
        meta["features"] = [granular]

    return idk.IsccMeta.construct(**meta)


def code_data(fp, **options):
    # type: (str|Path, Any) -> idk.IsccMeta
    """
    Create ISCC Data-Code.

    The Data-Code is a similarity preserving hash of the raw input data that allows for
    detection of similar binary data regardless of file format or metadata differences.

    :param fp: Filepath used for Data-Code creation.
    :key bits: Bit-length of the generated Data-Code UNIT. Default: 64
    :return: ISCC metadata including Data-Code.
    """
    fp = Path(fp)
    opts = idk.sdk_opts.override(options)
    with open(fp, "rb") as stream:
        meta = ic.gen_data_code_v0(stream, bits=opts.bits)

    return idk.IsccMeta.construct(**meta)


def code_instance(fp, **options):
    # type: (str|Path, Any) -> idk.IsccMeta
    """
    Create ISCC Instance-Code.

    The Instance-Code is a cryptographic hash (blake3) of the input data.
    Its purpose is to serve as a checksum that detects even minimal changes
    to the data of the referenced media asset. For cryptographically secure integrity
    checking, a full 256-bit multihash is provided with the `datahash` field.

    :param fp: Filepath used for Instance-Code creation.
    :key bits: Bit-length of the generated Instance-Code UNIT. Default: 64
    :return: ISCC metadata including Instance-Code, datahash and filesize.
    """
    fp = Path(fp)
    opts = idk.sdk_opts.override(options)
    with open(fp, "rb") as stream:
        meta = ic.gen_instance_code_v0(stream, bits=opts.bits)

    return idk.IsccMeta.construct(**meta)
