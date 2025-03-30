"""*EPUB handling module*."""

import io
import shutil
import tempfile
from pathlib import Path

import ebookmeta
from PIL import Image, ImageEnhance
import iscc_sdk as idk
import zipfile
import lxml
from loguru import logger as log


__all__ = [
    "epub_thumbnail",
    "epub_meta_embed",
    "epub_cover",
]


def epub_thumbnail(fp):
    # type: (str|Path) -> Image.Image
    """
    Creat thumbnail from EPUB document cover image.

    :param fp: Filepath to EPUB document.
    :return: Thumbnail image as PIL Image object
    """
    fp = Path(fp)
    # meta = ebookmeta.get_metadata(fp.as_posix())
    data = epub_cover(fp)
    img = Image.open(io.BytesIO(data))
    size = idk.sdk_opts.image_thumbnail_size
    img.thumbnail((size, size), resample=idk.LANCZOS)
    return ImageEnhance.Sharpness(img.convert("RGB")).enhance(1.4)


def epub_meta_embed(fp, meta):
    # type: (str|Path, idk.IsccMeta) -> str
    """
    Embed metadata into a copy of the EPUB file.

    :param fp: Filepath to source EPUB file
    :param IsccMeta meta: Metadata to embed into EPUB
    :return: Filepath to the new EPUB file with updated metadata
    """
    fp = Path(fp)
    tempdir = tempfile.mkdtemp()
    tempepub = shutil.copy(fp, tempdir)
    new_meta = ebookmeta.get_metadata(tempepub)
    if meta.name:
        new_meta.title = meta.name
    if meta.description:
        new_meta.description = meta.description
    if meta.creator:
        if isinstance(meta.creator, str):
            new_meta.set_author_list_from_string(meta.creator)
    ebookmeta.set_metadata(tempepub, new_meta)
    return tempepub


def epub_cover(fp):
    # type: (str|Path) -> bytes
    """
    Extract the cover image bytes from an EPUB file.

    This function attempts to locate the cover image by first checking the metadata
    cover reference, then falling back to scanning for image files with 'cover' in the name and
    if that fails it returns the first image file from the manifest.
    The function also logs the relative path to the image within the epub which was identified as
    cover image. If no image is found, it raises an error.

    :param fp: Filepath to EPUB file
    :return: Raw bytes of the cover image
    :raises IsccExtractionError: If no cover image can be found.
    """
    fp = Path(fp)
    cover_path = None
    image_paths = []

    try:
        with zipfile.ZipFile(fp, "r") as archive:
            # Find OPF file path from container.xml
            container_path = "META-INF/container.xml"
            if container_path not in archive.namelist():
                raise idk.IsccExtractionError(f"Missing {container_path} in {fp}")

            container_xml = archive.read(container_path)
            container_root = lxml.etree.fromstring(container_xml)
            opf_path = container_root.xpath(
                "//o:rootfile/@full-path",
                namespaces={"o": "urn:oasis:names:tc:opendocument:xmlns:container"},
            )[0]

            # Parse OPF file
            opf_xml = archive.read(opf_path)
            opf_root = lxml.etree.fromstring(opf_xml)
            opf_ns = {"opf": "http://www.idpf.org/2007/opf"}

            # 1. Check metadata for cover reference
            cover_id = opf_root.xpath(
                "//opf:metadata/opf:meta[@name='cover']/@content", namespaces=opf_ns
            )
            if cover_id:
                cover_id = cover_id[0]
                cover_href = opf_root.xpath(
                    f"//opf:manifest/opf:item[@id='{cover_id}']/@href", namespaces=opf_ns
                )
                if cover_href:
                    cover_path = Path(opf_path).parent / cover_href[0]
                    log.debug(f"Found cover image via metadata: {cover_path.as_posix()}")

            # 2. Scan manifest for images with 'cover' in the name
            if not cover_path:
                manifest_items = opf_root.xpath("//opf:manifest/opf:item", namespaces=opf_ns)
                for item in manifest_items:
                    media_type = item.get("media-type", "")
                    href = item.get("href")
                    if media_type.startswith("image/") and href:
                        item_path = (Path(opf_path).parent / href).as_posix()
                        image_paths.append(item_path)
                        if "cover" in href.lower():
                            cover_path = Path(item_path)
                            log.debug(
                                f"Found cover image via manifest scan: {cover_path.as_posix()}"
                            )
                            break

            # 3. Fallback to the first image in the manifest
            if not cover_path and image_paths:
                cover_path = Path(image_paths[0])
                log.debug(f"Using first image from manifest as cover: {cover_path.as_posix()}")

            if not cover_path:
                raise idk.IsccExtractionError(f"No cover image found in {fp}")

            # Ensure the path is relative to the archive root
            cover_path_str = cover_path.as_posix()
            if cover_path_str not in archive.namelist():
                # Try resolving relative paths if needed (though Path should handle this)
                # This part might need adjustment based on EPUB structure variations
                log.warning(
                    f"Cover path {cover_path_str} not directly in archive, attempting resolution."
                )
                # Basic check if it exists at all
                found = False
                for name in archive.namelist():
                    if name.endswith(cover_path.name):
                        cover_path_str = name
                        found = True
                        log.debug(f"Resolved cover path to {cover_path_str}")
                        break
                if not found:
                    raise idk.IsccExtractionError(
                        f"Cover image path {cover_path_str} not found in archive {fp}"
                    )

            # Extract image bytes
            return archive.read(cover_path_str)

    except zipfile.BadZipFile:
        raise idk.IsccExtractionError(f"Invalid EPUB (Zip) file: {fp}")
    except (lxml.etree.XMLSyntaxError, IndexError) as e:
        raise idk.IsccExtractionError(f"Failed to parse EPUB metadata for {fp}: {e}")
    except KeyError as e:
        raise idk.IsccExtractionError(f"Cover image file {e} not found within EPUB archive {fp}")
