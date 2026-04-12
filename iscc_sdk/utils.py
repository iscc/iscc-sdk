import mimetypes
import posixpath
import re
import shutil
import tempfile
import time
from functools import cache
from importlib import metadata
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from loguru import logger as log


__all__ = [
    "DownloadFile",
    "TempFile",
    "is_url",
    "timer",
    "is_installed",
]


def is_url(text):
    # type: (str) -> bool
    """Check if text is an HTTP or HTTPS URL."""
    try:
        parsed = urlparse(str(text))
        return parsed.scheme in ("http", "https")
    except Exception:
        return False


def _filename_from_url(url, headers=None):
    # type: (str, Any) -> str
    """Extract a safe filename from URL path or Content-Disposition header.

    The returned filename is always a plain basename with no directory components,
    preventing path traversal when joined with a temp directory path.

    :param url: The URL to extract the filename from.
    :param headers: Optional HTTP response headers.
    :return: Sanitized filename or "download" as fallback.
    """
    filename = ""

    # Try Content-Disposition header first
    if headers:
        content_disp = headers.get("Content-Disposition", "")
        # Match quoted filenames (may contain spaces) or unquoted tokens
        match = re.search(r'filename="([^"]+)"|filename=([^;\s]+)', content_disp)
        if match:
            filename = match.group(1) or match.group(2) or ""

    # Fall back to URL path
    if not filename:
        parsed = urlparse(url)
        filename = posixpath.basename(parsed.path)

    # Sanitize: strip directory components and use only the final basename
    filename = Path(filename).name
    return filename or "download"


def _add_ext_from_content(temp_path, content_type=""):
    # type: (Path, str) -> Path
    """Add a file extension to an extensionless file based on its content or Content-Type.

    Content sniffing (magic bytes) is tried first. The Content-Type header is only used
    as a fallback when sniffing returns application/octet-stream, avoiding misclassification
    from inaccurate server headers.

    :param temp_path: Path to the downloaded file.
    :param content_type: Content-Type header value from the HTTP response.
    :return: Path with extension added (file is renamed), or original path if unchanged.
    """
    import magic

    with open(temp_path, "rb") as f:
        try:
            sniffed = magic.from_buffer(f.read(4096), mime=True)
        except Exception:
            sniffed = None

    mime = sniffed
    if not sniffed or sniffed == "application/octet-stream":
        # Content sniffing failed — fall back to Content-Type header
        mime = content_type.split(";")[0].strip() if content_type else ""

    if mime and mime != "application/octet-stream":
        ext = mimetypes.guess_extension(mime, strict=False)
        if ext:
            new_path = temp_path.parent / (temp_path.name + ext)
            temp_path.rename(new_path)
            return new_path

    return temp_path


class DownloadFile:
    """Context manager that downloads a URL to a temporary file.

    The original filename from the URL is preserved so that mediatype detection
    based on file extensions works correctly.

    Usage::

        with DownloadFile("https://example.com/document.pdf") as tmp:
            result = code_iscc(tmp.as_posix())
    """

    def __init__(self, url):
        # type: (str) -> None
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            raise ValueError(f"Only HTTP and HTTPS URLs are supported, got: {parsed.scheme!r}")
        self.url = url
        self.temp_dir = None  # type: Path | None

    def __enter__(self):
        # type: () -> Path
        self.temp_dir = Path(tempfile.mkdtemp())
        ua = f"iscc-sdk/{metadata.version('iscc-sdk')} (+https://github.com/iscc/iscc-sdk)"
        req = Request(self.url, headers={"User-Agent": ua})  # noqa: S310
        log.info(f"Downloading {self.url}")
        with urlopen(req, timeout=60) as response:  # noqa: S310
            # Use final URL after redirects for better filename/extension detection
            filename = _filename_from_url(response.geturl(), response.headers)
            content_type = response.headers.get("Content-Type", "")
            temp_path = self.temp_dir / filename
            with open(temp_path, "wb") as f:
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
        # Add extension from content sniffing (or Content-Type fallback) for
        # extensionless files so that mediatype detection works correctly.
        if not temp_path.suffix:
            temp_path = _add_ext_from_content(temp_path, content_type)
        log.info(f"Downloaded to {temp_path}")
        return temp_path

    def __exit__(self, exc_type, exc_value, traceback):
        if self.temp_dir:
            shutil.rmtree(self.temp_dir)


class TempFile:
    def __init__(self, original_path):
        # type: (str|Path) -> None
        self.original_path = Path(original_path)
        self.temp_dir: Path | None = None

    def __enter__(self):
        # type: () -> Path
        self.temp_dir = Path(tempfile.mkdtemp())
        temp_filename = self.temp_dir / self.original_path.name
        shutil.copy2(self.original_path, temp_filename)
        return temp_filename

    def __exit__(self, exc_type, exc_value, traceback):
        shutil.rmtree(self.temp_dir)


class timer:
    def __init__(self, message: str):
        self.message = message

    def __enter__(self):
        # Record the start time
        self.start_time = time.perf_counter()

    def __exit__(self, exc_type, exc_value, traceback):
        # Calculate the elapsed time
        elapsed_time = time.perf_counter() - self.start_time
        # Log the message with the elapsed time
        log.debug(f"{self.message} {elapsed_time:.4f} seconds")


@cache
def is_installed(package_name):
    # type: (str) -> bool
    """
    Check if a Python package is installed.

    :param str package_name: The name of the package to check
    :return: True if the package is installed, False otherwise
    :rtype: bool
    """
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False
