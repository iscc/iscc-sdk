"""*Video handling module*"""

import os
from typing import Tuple, List, Optional
from loguru import logger as log
import io
import sys
import tempfile
from os.path import join, basename
from pathlib import Path
from secrets import token_hex
from PIL import Image, ImageEnhance
import iscc_sdk as idk
import iscc_core as ic


__all__ = [
    "video_meta_extract",
    "video_meta_embed",
    "video_thumbnail",
    "video_mp7sig_extract",
    "video_mp7sig_extract_scenes",
    "video_features_extract",
    "video_parse_scenes",
    "video_compute_granular",
]

VIDEO_META_MAP = {
    "iscc_name": "name",
    "iscc_description": "description",
    "iscc_meta": "meta",
    "title": "name",
    "track": "name",
    "show": "name",
    "album": "name",
    "description": "description",
    "synopsis": "description",
    "comment": "description",
    "author": "creator",
    "composer": "creator",
    "artist": "creator",
    "album_artist": "creator",
    "copyright": "rights",
    "license": "license",
    "acquire": "acquire",
}


def video_meta_extract(fp):
    # type: (str) -> dict
    """
    Extract metadata from video.

    :param str fp: Filepath to video file
    :return: Metdata mpped to IsccMeta schema
    :rtype: dict
    """

    args = ["-i", fp, "-movflags", "use_metadata_tags", "-f", "ffmetadata", "-"]

    result = idk.run_ffmpeg(args)
    encoding = sys.stdout.encoding or "utf-8"
    text = result.stdout.decode(encoding, errors="ignore")

    # parse metadata
    meta = dict()
    for line in text.splitlines(keepends=False):
        if not line.startswith(";FFMETA"):
            key, value = line.split("=", 1)
            if value:
                meta[key.lower()] = (
                    value.replace(r"\=", "=")
                    .replace(r"\;", ";")
                    .replace(r"\#", "#")
                    .replace(r"\;", ";")
                    .replace(r"\\n", "\n")
                    .replace(r"\\", "\\")
                )

    # map metadata
    mapped = dict()
    done = set()
    for tag, mapped_field in VIDEO_META_MAP.items():
        if mapped_field in done:
            continue
        value = meta.get(tag)
        if value:
            log.debug(f"Mapping video metadata: {tag} -> {mapped_field} -> {value}")
            mapped[mapped_field] = value
            done.add(mapped_field)
    return mapped


def video_meta_embed(fp, meta):
    # type: (str, idk.IsccMeta) -> str
    """
    Embed metadata into a copy of the video file.

    Supported fields: name, description, meta, creator, license, aquire

    :param str fp: Filepath to source video file
    :param IsccMeta meta: Metadata to embed into video
    :return: Filepath to new video file with updated metadata
    :rtype: str
    """

    write_map = {
        "name": "iscc_name",
        "description": "iscc_description",
        "meta": "iscc_meta",
        "creator": "author",
        "rights": "copyright",
        "license": "license",
        "acquire": "acquire",
    }

    # Metadata keys or values containing special characters (‘=’, ‘;’, ‘#’, ‘\’ and a newline)
    # must be escaped with a backslash ‘\’.
    escape = str.maketrans(
        {
            "=": r"\=",
            ";": r"\;",
            "#": r"\#",
            "\\": r"\\",
            "\n": r"\\n",
        }
    )

    # Prepare metadata file
    cmdf = ";FFMETADATA1\n"
    for field in write_map.keys():
        value = getattr(meta, field)
        if value:
            value = value.translate(escape)
            cmdf += f"{write_map[field]}={value}\n"

    # Create temp filepaths
    tempdir = tempfile.mkdtemp()
    metafile = join(tempdir, "meta.txt")
    videofile = join(tempdir, basename(fp))

    # Store metadata
    with open(metafile, "wt", encoding="utf-8") as outf:
        outf.write(cmdf)

    # Embed metadata
    # See: http://ffmpeg.org/ffmpeg-formats.html#Metadata-1
    args = [
        "-i",
        fp,
        "-i",
        metafile,
        "-movflags",
        "use_metadata_tags",
        "-map_metadata",
        "1",
        "-codec",
        "copy",
        videofile,
    ]
    idk.run_ffmpeg(args)
    return videofile


def video_thumbnail(fp):
    # type: (str) -> Optional[Image.Image]
    """
    Create a thumbnail for a video.

    :param str fp: Filepath to video file.
    :return: Raw PNG byte data
    :rtype: bytes
    """
    size = idk.sdk_opts.image_thumbnail_size

    args = [
        "-i",
        fp,
        "-vf",
        f"thumbnail,scale={size}:-1",
        "-frames:v",
        "1",
        "-c:v",
        "png",
        "-f",
        "image2pipe",
        "-",
    ]
    try:
        result = idk.run_ffmpeg(args)
    except Exception as e:
        log.error(f"Failed video thumbnail extraction: {e}")
        return None
    img_obj = Image.open(io.BytesIO(result.stdout))
    return ImageEnhance.Sharpness(img_obj.convert("RGB")).enhance(1.4)


def video_features_extract(fp):
    # type: (str) -> List[Tuple[int, ...]]
    """
    Extract video features.

    :param str fp: Filepath to video file.
    :return: A sequence of frame signatures.
    :rtype: Sequence[Tuple[int, ...]]
    """
    # TODO use confidence value to improve simililarity hash.
    sig = video_mp7sig_extract(fp)

    if idk.sdk_opts.video_store_mp7sig:
        outp = fp + ".iscc.mp7sig"
        with open(outp, "wb") as outf:
            outf.write(sig)

    frames = idk.read_mp7_signature(sig)
    return [tuple(frame.vector.tolist()) for frame in frames]


def video_mp7sig_extract(fp):
    # type: (str) -> bytes
    """Extract MPEG-7 Video Signature.

    :param str fp: Filepath to video file.
    :return: raw signature data
    :rtype: bytes
    """

    sigfile_path = Path(tempfile.mkdtemp(), token_hex(16) + ".bin")
    sigfile_path_escaped = sigfile_path.as_posix().replace(":", "\\\\:")

    # Extract MP7 Signature
    vf = f"signature=format=binary:filename={sigfile_path_escaped}"
    vf = f"fps=fps={idk.sdk_opts.video_fps}," + vf
    args = ["-i", fp, "-vf", vf, "-f", "null", "-"]
    idk.run_ffmpeg(args)

    with open(sigfile_path, "rb") as sig:
        sigdata = sig.read()
    os.remove(sigfile_path)
    return sigdata


def video_mp7sig_extract_scenes(fp, scene_limit=None):
    """Extract MPEG-7 Video Signature and Scenes.

    :param str fp: Filepath to video file.
    :param Optional[float] scene_limit: Threshold value above which a scene cut is created (0.4)
    :return: raw signature data
    :rtype: bytes
    """

    scene_limit = scene_limit or idk.sdk_opts.video_scene_limit

    sigfile_path = Path(tempfile.mkdtemp(), token_hex(16) + ".bin")
    sigfile_path_escaped = sigfile_path.as_posix().replace(":", "\\\\:")

    scene_path = Path(tempfile.mkdtemp(), token_hex(16) + ".cut")
    scene_path_escaped = scene_path.as_posix().replace(":", "\\\\:")

    sig_cmd = f"signature=format=binary:filename={sigfile_path_escaped}"
    sig_cmd = f"fps=fps={idk.sdk_opts.video_fps}," + sig_cmd
    scene_cmd = f"select='gte(scene,0)',metadata=print:file={scene_path_escaped}"

    args = [
        "-i",
        fp,
        "-an",
        "-sn",
        "-filter_complex",
        f"split[in1][in2];[in1]{scene_cmd}[out1];[in2]{sig_cmd}[out2]",
        "-map",
        "[out1]",
        "-f",
        "null",
        "-",
        "-map",
        "[out2]",
        "-f",
        "null",
        "-",
    ]

    idk.run_ffmpeg(args)

    with open(sigfile_path, "rb") as sig:
        sigdata = sig.read()
    os.remove(sigfile_path)

    with open(scene_path, "rt", encoding="utf-8") as scenein:
        scenetext = scenein.read()
    os.remove(scene_path)

    scenes = video_parse_scenes(scenetext, scene_limit)

    return sigdata, scenes


def video_parse_scenes(scene_text, scene_limit=None):
    # type: (str) -> List[float]
    """Parse scene score output from ffmpeg

    :param str scene_text: Scene score output from ffmpeg
    :param Optional[float] scene_limit: Threshold value above which a scene cut is created (0.4)
    """

    scene_limit = scene_limit or idk.sdk_opts.video_scene_limit

    if not scene_text.strip():
        return []

    times = []
    scores = []
    for line in scene_text.splitlines():
        if line.startswith("frame:"):
            ts = round(float(line.split()[-1].split(":")[-1]), 3)
            times.append(ts)
        if line.startswith("lavfi.scene_score"):
            scores.append(float(line.split("=")[-1]))

    cutpoints = []
    for ts, score in zip(times, scores):
        if score >= scene_limit:
            cutpoints.append(ts)

    # append last frame timestamp if not in cutpoints
    if cutpoints and cutpoints[-1] != times[-1]:
        cutpoints.append(times[-1])

    return cutpoints[1:]


def video_compute_granular(frames, scenes):
    # type: (List[idk.Frame], List[float]) -> dict
    """Compute video signatures for individual scenes in video.
    Returns a dictionary conforming to `shema.Feature`- objects.
    """
    features, sizes, segment = [], [], []
    start_frame = 0
    for cidx, cutpoint in enumerate(scenes):
        try:
            frames = frames[start_frame:]
        except IndexError:  # pragma: no cover
            break
        for fidx, frame in enumerate(frames):
            frame_t = tuple(frame.vector.tolist())
            segment.append(frame_t)
            if frame.elapsed >= cutpoint:
                features.append(ic.encode_base64(ic.soft_hash_video_v0(segment, 64)))
                segment = []
                prev_cutpoint = 0 if cidx == 0 else scenes[cidx - 1]
                duration = round(cutpoint - prev_cutpoint, 3)
                sizes.append(duration)
                start_frame = fidx + 1
                break
    if not features:
        log.info("No scenes detected. Use all frames")
        segment = [tuple(frame.vector.tolist()) for frame in frames]
        features = [ic.encode_base64(ic.soft_hash_video_v0(segment, 64))]
        sizes = [round(float(frames[-1].elapsed), 3)]

    return dict(kind="video", version=0, features=features, sizes=sizes)
