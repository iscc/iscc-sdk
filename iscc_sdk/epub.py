"""*EPUB handling module*."""

import io
import shutil
import tempfile
from pathlib import Path
from typing import Any, List

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


def epub_cover(fp):  # pragma: no cover
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


def epub_process_container(fp, **options):
    # type: (str|Path, Any) -> List[idk.IsccMeta]
    """
    Extract and process images from EPUB file.
    Skips processing for fixed layout EPUBs.

    :param fp: Filepath to EPUB file
    :param options: Processing options
    :return: List of IsccMeta objects for embedded images
    """
    fp = Path(fp)
    parts = []

    # Check if the EPUB is fixed layout
    if is_fixed_layout_epub(fp):  # pragma: no cover
        log.info(f"Skipping container processing for fixed layout EPUB: {fp.name}")
        return parts

    with tempfile.TemporaryDirectory() as temp_dir:
        # Extract images from EPUB
        images = epub_extract_images(fp, temp_dir)

        # Process each image
        for img_path in images:
            try:
                # Generate ISCC for each image
                img_meta = idk.code_iscc(img_path, **options)
                parts.append(img_meta.dict())
            except Exception as e:  # pragma: no cover
                log.warning(f"Failed to process embedded image {img_path.name}: {e}")

    return parts


def epub_extract_images(fp, output_dir):
    # type: (str|Path, str|Path) -> List[Path]
    """
    Extract images from EPUB file to output directory where both
    width and height are >= min_image_size.

    :param fp: Filepath to EPUB file
    :param output_dir: Directory to extract images to
    :return: List of paths to extracted images
    """
    fp = Path(fp)
    output_dir = Path(output_dir)
    extracted_images = []
    min_size = idk.sdk_opts.min_image_size

    with zipfile.ZipFile(fp, "r") as archive:
        # Identify image files in the archive
        for item in archive.namelist():
            if item.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")):
                # Extract the image
                img_data = archive.read(item)

                # Check image dimensions before extracting
                try:
                    img = Image.open(io.BytesIO(img_data))
                    width, height = img.size

                    # Only extract if both dimensions are >= min_size
                    if width >= min_size and height >= min_size:
                        img_filename = Path(item).name
                        img_path = output_dir / img_filename

                        # Write to temp file
                        with open(img_path, "wb") as img_file:
                            img_file.write(img_data)

                        extracted_images.append(img_path)
                except Exception as e:  # pragma: no cover
                    log.warning(f"Failed to process image {item} from EPUB: {e}")

    return extracted_images


def is_fixed_layout_epub(fp):  # pragma: no cover
    # type: (str|Path) -> bool
    """
    Check if an EPUB is a fixed layout publication.

    :param fp: Path to EPUB file
    :return: True if the EPUB is fixed layout, False otherwise
    """
    fp = Path(fp)

    try:
        with zipfile.ZipFile(fp, "r") as archive:
            # Find OPF file path from container.xml
            container_path = "META-INF/container.xml"
            if container_path not in archive.namelist():
                log.warning(f"Missing {container_path} in {fp}")
                return False

            container_xml = archive.read(container_path)
            container_root = lxml.etree.fromstring(container_xml)
            opf_path = container_root.xpath(
                "//o:rootfile/@full-path",
                namespaces={"o": "urn:oasis:names:tc:opendocument:xmlns:container"},
            )[0]

            # Parse OPF file
            opf_xml = archive.read(opf_path)
            opf_root = lxml.etree.fromstring(opf_xml)

            # Define necessary namespaces for XPath queries
            namespaces = {
                "opf": "http://www.idpf.org/2007/opf",
                "dc": "http://purl.org/dc/elements/1.1/",
            }

            # Check for fixed layout indicators in metadata
            # Method 1: EPUB 3.0 standard - using namespaces
            fixed_layout = opf_root.xpath(
                "//opf:metadata/opf:meta[@property='rendition:layout' and text()='pre-paginated']",
                namespaces=namespaces,
            )
            if fixed_layout:
                return True

            # Method 2: Alternative specification - using namespaces
            fixed_layout = opf_root.xpath(
                "//opf:metadata/opf:meta[@name='fixed-layout' and (@content='true' or @content='yes')]",
                namespaces=namespaces,
            )
            if fixed_layout:
                return True

            # Method 3: Some EPUBs might use meta elements without explicit namespace
            fixed_layout = opf_root.xpath(
                "//meta[@property='rendition:layout' and text()='pre-paginated']"
            )
            if fixed_layout:
                return True

            fixed_layout = opf_root.xpath(
                "//meta[@name='fixed-layout' and (@content='true' or @content='yes')]"
            )
            if fixed_layout:
                return True

            return False

    except Exception as e:
        log.warning(f"Error checking if EPUB is fixed layout: {e}")
        return False


# Register EPUB container processor
idk.register_container_processor("application/epub+zip", epub_process_container)
