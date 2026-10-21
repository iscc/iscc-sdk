"""*Audio handling module*."""

import json
import shutil
import tempfile
from pathlib import Path

import taglib
from loguru import logger as log
from PIL import Image, ImageEnhance

import iscc_sdk as idk

__all__ = [
    "audio_features_extract",
    "audio_meta_embed",
    "audio_meta_extract",
    "audio_thumbnail",
]


AUDIO_META_MAP = {
    "ISCC:NAME": "name",
    "ISCC:DESCRIPTION": "description",
    "ISCC:META": "meta",
    "ISCC:LICENSE": "license",
    "ISCC:ACQUIRE": "acquire",
    "ISCC_NAME": "name",
    "ISCC_DESCRIPTION": "description",
    "ISCC_META": "meta",
    "ISCC_LICENSE": "license",
    "ISCC_ACQUIRE": "acquire",
    "TITLE": "name",
    # "ALBUM": "album",
    # "GENRE": "genre",
    "COMPOSER": "creator",
    "ORIGINALARTIST": "creator",
    "ARTIST": "creator",
    "ALBUMARTIST": "creator",
    "LICENSE": "license",
    "COPYRIGHT": "rights",
    "LANGUAGE": "language",
    "URL": "acquire",
    "ARTISTWEBPAGE": "acquire",
}


def audio_thumbnail(fp, **options):
    # type: (str|Path, Any) -> Image.Image|None
    """
    Create a thumbnail from embedded cover art.

    :param fp: Filepath to audio file.
    :param options: Keyword arguments forwarded to ``sdk_opts``:
        **image_thumbnail_size** - Size of the larger side of the thumbnail in pixels. Default: 128
    :return: Thumbnail image as PIL Image object
    """
    fp = Path(fp)
    tempdir = Path(tempfile.mkdtemp())
    tempimg = tempdir / "cover.jpg"
    cmd = ["-i", fp, "-an", "-vcodec", "copy", tempimg]
    size = idk.sdk_opts.override(options).image_thumbnail_size
    try:
        idk.run_ffmpeg(cmd)
        img = Image.open(tempimg)
    except Exception:
        img = None
    if img:
        img.thumbnail((size, size), resample=idk.LANCZOS)
        img = ImageEnhance.Sharpness(img.convert("RGB")).enhance(1.4)

    shutil.rmtree(tempdir, ignore_errors=True)
    return img


def audio_meta_extract(fp):
    # type: (str|Path) -> dict
    """
    Extract metadata from audio file.

    :param fp: Filepath to audio file.
    :return: Metadata mapped to IsccMeta schema
    """
    fp = Path(fp)
    mapped = dict()
    done = set()

    try:
        obj = taglib.File(fp)
        meta = dict(obj.tags)
        mapped["duration"] = round(obj.length)
        obj.close()
    except OSError as e:  # pragma: no cover
        # This is a workaround for the issue that taglib requires exclusive access even for reading.
        log.warning(f"Create tempfile for taglib access {fp.name}: {e}")
        try:
            with idk.TempFile(fp) as tmp_path:
                obj = taglib.File(tmp_path.as_posix())
                meta = dict(obj.tags)
                mapped["duration"] = round(obj.length)
                obj.close()
        except Exception as e:
            log.warning(f"Failed metadata extraction for {fp.name}: {e}")
            return mapped

    for tag, mapped_field in AUDIO_META_MAP.items():
        if mapped_field in done:
            continue
        value = meta.get(tag)
        if value:
            log.debug(f"Mapping audio metadata: {tag} -> {mapped_field} -> {value[0]}")
            mapped[mapped_field] = value[0]
            done.add(mapped_field)
    # Todo - add bitrate, channels, samplerate to iscc-schema
    # mapped["bitrate"] = obj.bitrate
    # mapped["channels"] = obj.channels
    # mapped["samplerate"] = obj.sampleRate
    return mapped


def audio_meta_embed(fp, meta):
    # type: (str|Path, idk.IsccMeta) -> str
    """
    Embed metadata into a copy of the audio file.

    :param fp: Filepath to source audio file
    :param IsccMeta meta: Metadata to embed into audio file
    :return: Filepath to new audio file with updated metadata
    """
    fp = Path(fp)
    # TagLib silently drops MP4 tag names that contain a colon
    sep = "_" if idk.mediatype_and_mode(fp)[0] == "audio/mp4" else ":"
    tdir = tempfile.mkdtemp()
    tfile = shutil.copy(fp, tdir)
    obj = taglib.File(tfile)
    if meta.name:
        obj.tags["TITLE"] = [meta.name]
        obj.tags[f"ISCC{sep}NAME"] = [meta.name]
    if meta.description:
        obj.tags[f"ISCC{sep}DESCRIPTION"] = [meta.description]
    if meta.meta:
        obj.tags[f"ISCC{sep}META"] = [meta.meta]
    if meta.license:
        obj.tags[f"ISCC{sep}LICENSE"] = [meta.license]
    if meta.acquire:
        obj.tags[f"ISCC{sep}ACQUIRE"] = [meta.acquire]
    obj.save()
    obj.close()
    return tfile


def audio_features_extract(fp):
    # type: (str|Path) -> dict
    """
    Exctracts chromprint fingerprint.

    :param fp: Filepath
    :return: A dict with `duration` in seconds and `fingerprint` 32-bit integers
    """
    fp = Path(fp)
    args = ["-raw", "-json", "-signed", "-length", "0", fp]
    proc = idk.run_fpcalc(args)
    result = json.loads(proc.stdout)
    return result
