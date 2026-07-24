"""*Manage SDK binary media file handling tools*."""

import os
import shutil
import stat
import subprocess
import tarfile
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from platform import architecture, system
from urllib.parse import urlparse
from urllib.request import urlretrieve

from blake3 import blake3
from loguru import logger as log

import iscc_sdk as idk

__all__ = [
    "install",
    "run_ffmpeg",
    "run_ffprobe",
    "run_fpcalc",
]

BASE_VERSION = "1.0.0"
BASE_URL = f"https://github.com/iscc/iscc-binaries/releases/download/v{BASE_VERSION}"

FFPROBE_VERSION = "8.1"
FFPROBE_URLS = {
    "windows-64": f"{BASE_URL}/ffprobe-{FFPROBE_VERSION}-win-64.zip",
    "linux-64": f"{BASE_URL}/ffprobe-{FFPROBE_VERSION}-linux-64.zip",
    "darwin-64": f"{BASE_URL}/ffprobe-{FFPROBE_VERSION}-macos-64.zip",
}
FFPROBE_CHECKSUMS = {
    "linux-64": "5d4768df3c5d3f25863bf801d2545867a5b232d7fd94acb22625c08691c1697d",
    "darwin-64": "c281052b0eace0d64bf85334b91005a52d2a622c5e43eda0e2e72b88de2e2c4b",
    "windows-64": "e96fd1ab1b26c3f943e0fb4a89cb7fb601bbf1ba12fcf8414ff13cbdad6f4c5d",
}

FFMPEG_VERSION = "8.1"
FFMPEG_URLS = {
    "windows-64": f"{BASE_URL}/ffmpeg-{FFMPEG_VERSION}-win-64.zip",
    "linux-64": f"{BASE_URL}/ffmpeg-{FFMPEG_VERSION}-linux-64.zip",
    "darwin-64": f"{BASE_URL}/ffmpeg-{FFMPEG_VERSION}-macos-64.zip",
}
FFMPEG_CHECKSUMS = {
    "linux-64": "9a49dc5c1d7720acee5e269565f2674d8bb6a08fa9b428cfb173c5ff22188b45",
    "darwin-64": "abc4ddf4f0fa0273ab635cde87cbaa02b71caa0fb77cd93a29e6945a8c17758d",
    "windows-64": "d84c72395b9f52cf34c516fdfab83edfa631165b32ab1674ed0f4686989e1126",
}

FPCALC_VERSION = "1.6.0"
FPCALC_URLS = {
    "windows-64": f"{BASE_URL}/chromaprint-fpcalc-{FPCALC_VERSION}-windows-x86_64.zip",
    "linux-64": f"{BASE_URL}/chromaprint-fpcalc-{FPCALC_VERSION}-linux-x86_64.tar.gz",
    "darwin-64": f"{BASE_URL}/chromaprint-fpcalc-{FPCALC_VERSION}-macos-x86_64.tar.gz",
}
FPCALC_CHECKSUMS = {
    "windows-64": "2514e29aa194d25e199d3ba2721964526126ff4ce6b8e8ad21b9186b92d0b363",
    "linux-64": "4a39891188fd6d739a41fdb84022a03f0f6cd04dd10b7f02cd9ab85ee3fa8145",
    "darwin-64": "0c4c27715752308ba7b4adc01597cf9f9e76f0023ba281a6cd7827b7bcbae93e",
}


def install():
    """Install binary tools for content extraction and metadata handling."""
    with ThreadPoolExecutor(max_workers=6) as p:
        p.submit(fpcalc_install)
        p.submit(ffprobe_install)
        p.submit(ffmpeg_install)
    return True


def system_tag():
    os_tag = system().lower()
    os_bits = architecture()[0].rstrip("bit")
    return f"{os_tag}-{os_bits}"


def is_installed(fp: str) -> bool:
    """Check if binary at `fp` exists and is executable."""
    return os.path.isfile(fp) and os.access(fp, os.X_OK)


def extract(archive):  # pragma: no cover
    """Extract downloded archive."""

    if archive.endswith(".zip"):
        with zipfile.ZipFile(archive, "r") as zip_file:
            zip_file.extractall(Path(archive).parent.absolute())

    elif archive.endswith("tar.gz"):
        with tarfile.open(archive, "r:gz") as tar_file:

            def is_within_directory(directory, target):
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)

                prefix = os.path.commonprefix([abs_directory, abs_target])

                return prefix == abs_directory

            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")

                tar.extractall(path, members, numeric_owner=numeric_owner)

            safe_extract(tar_file, Path(archive).parent.absolute())
    os.unlink(archive)


########################################################################################
# Fpcalc                                                                               #
########################################################################################


def fpcalc_bin():  # pragma: no cover
    """Returns local path to fpcalc executable."""
    if system() == "Windows":
        return os.path.join(idk.dirs.user_data_dir, f"fpcalc-{FPCALC_VERSION}.exe")
    return os.path.join(idk.dirs.user_data_dir, f"fpcalc-{FPCALC_VERSION}")


def fpcalc_is_installed():  # pragma: no cover
    """Check if fpcalc is installed."""
    fp = fpcalc_bin()
    return os.path.isfile(fp) and os.access(fp, os.X_OK)


def fpcalc_download_url():
    """Return system and version dependent download url."""
    return FPCALC_URLS[system_tag()]


def fpcalc_download():  # pragma: no cover
    """Download fpcalc and return path to archive file."""
    b3 = FPCALC_CHECKSUMS.get(system_tag())
    return download_file(fpcalc_download_url(), checksum=b3)


def fpcalc_extract(archive):  # pragma: no cover
    """Extract archive with fpcalc executable."""
    if archive.endswith(".zip"):
        with zipfile.ZipFile(archive, "r") as zip_file:
            for member in zip_file.namelist():
                filename = os.path.basename(member)
                if filename == "fpcalc.exe":
                    source = zip_file.open(member)
                    target = open(fpcalc_bin(), "wb")
                    with source, target:
                        shutil.copyfileobj(source, target)
    elif archive.endswith("tar.gz"):
        with tarfile.open(archive, "r:gz") as tar_file:
            for member in tar_file.getmembers():
                if member.isfile() and member.name.endswith("fpcalc"):
                    source = tar_file.extractfile(member)
                    target = open(fpcalc_bin(), "wb")
                    with source, target:
                        shutil.copyfileobj(source, target)
    os.unlink(archive)


def fpcalc_install():  # pragma: no cover
    """Install fpcalc command line tool and return path to executable."""
    if fpcalc_is_installed():
        log.debug("Fpcalc is already installed.")
        return fpcalc_bin()
    log.critical("installing fpcalc")
    archive_path = fpcalc_download()
    fpcalc_extract(archive_path)
    st = os.stat(fpcalc_bin())
    os.chmod(fpcalc_bin(), st.st_mode | stat.S_IEXEC)
    return fpcalc_bin()


def fpcalc_version_info():  # pragma: no cover
    """Get fpcalc version."""
    try:
        r = subprocess.run([fpcalc_bin(), "-v"], stdout=subprocess.PIPE)
        return r.stdout.decode("utf-8").strip().split()[2]
    except FileNotFoundError:
        return "FPCALC not installed"


def run_fpcalc(args: list[str | Path]):
    """Run fpcalc command with `args`. Installs fpcalc if not found."""
    cmd = [fpcalc_bin()] + [str(a) for a in args]
    try:
        result = subprocess.run(cmd, capture_output=True, check=True)
    except FileNotFoundError:  # pragma: no cover
        print("FPCALC not found - installing ...")
        fpcalc_install()
        result = subprocess.run(cmd, capture_output=True, check=True)
    return result


########################################################################################
# ffprobe                                                                              #
########################################################################################


def ffprobe_download_url():
    """Return system dependent download url."""
    return FFPROBE_URLS[system_tag()]


def ffprobe_bin() -> str:
    """Returns local path to ffprobe executable."""
    path = os.path.join(idk.dirs.user_data_dir, f"ffprobe-{FFPROBE_VERSION}")
    if system() == "Windows":
        path += ".exe"
    return path


def ffprobe_download():  # pragma: no cover
    """Download ffprobe and return path to archive file."""
    b3 = FFPROBE_CHECKSUMS.get(system_tag())
    return download_file(ffprobe_download_url(), checksum=b3)


def ffprobe_extract(archive: str):  # pragma: no cover
    """Extract ffprobe from archive."""
    fname = "ffprobe.exe" if system() == "Windows" else "ffprobe"
    with zipfile.ZipFile(archive) as zip_file:
        with zip_file.open(fname) as zf, open(ffprobe_bin(), "wb") as lf:
            shutil.copyfileobj(zf, lf)
    os.unlink(archive)


def ffprobe_install():  # pragma: no cover
    """Install ffprobe command line tool and return path to executable."""
    if is_installed(ffprobe_bin()):
        log.debug("ffprobe is already installed")
        return ffprobe_bin()
    log.critical("installing ffprobe")
    archive_path = ffprobe_download()
    ffprobe_extract(archive_path)
    st = os.stat(ffprobe_bin())
    os.chmod(ffprobe_bin(), st.st_mode | stat.S_IEXEC)
    assert is_installed(ffprobe_bin())
    return ffprobe_bin()


def ffprobe_version_info():  # pragma: no cover
    """Get ffprobe version"""
    try:
        r = subprocess.run([ffprobe_bin(), "-version"], stdout=subprocess.PIPE)
        return (
            r.stdout.decode("utf-8")
            .strip()
            .splitlines()[0]
            .split()[2]
            .rstrip("-static")
            .rstrip("-tessu")
        )
    except FileNotFoundError:
        return "ffprobe not installed"


def run_ffprobe(args: list[str | Path]):  # pragma: no cover
    """Run ffprobe command with `args`. Install ffprobe if not found."""
    cmd = [ffprobe_bin()] + [str(a) for a in args]
    try:
        result = subprocess.run(cmd, capture_output=True, check=True)
    except FileNotFoundError:  # pragma: no cover
        print("FFPROBE not found - installing ...")
        ffprobe_install()
        result = subprocess.run(cmd, capture_output=True, check=True)
    return result


########################################################################################
# ffmpeg                                                                               #
########################################################################################


def ffmpeg_download_url():
    """Return system dependent download url."""
    return FFMPEG_URLS[system_tag()]


def ffmpeg_bin() -> str:
    """Returns local path to ffmpeg executable."""
    path = os.path.join(idk.dirs.user_data_dir, f"ffmpeg-{FFMPEG_VERSION}")
    if system() == "Windows":
        path += ".exe"
    return path


def ffmpeg_download():  # pragma: no cover
    """Download ffmpeg and return path to archive file."""
    b3 = FFMPEG_CHECKSUMS.get(system_tag())
    return download_file(ffmpeg_download_url(), checksum=b3)


def ffmpeg_extract(archive: str):  # pragma: no cover
    """Extract ffmpeg from archive."""
    fname = "ffmpeg.exe" if system() == "Windows" else "ffmpeg"
    with zipfile.ZipFile(archive) as zip_file:
        with zip_file.open(fname) as zf, open(ffmpeg_bin(), "wb") as lf:
            shutil.copyfileobj(zf, lf)
    os.unlink(archive)


def ffmpeg_install():  # pragma: no cover
    """Install ffmpeg command line tool and return path to executable."""
    if is_installed(ffmpeg_bin()):
        log.debug("ffmpeg is already installed")
        return ffmpeg_bin()
    log.critical("installing ffmpeg")
    archive_path = ffmpeg_download()
    ffmpeg_extract(archive_path)
    st = os.stat(ffmpeg_bin())
    os.chmod(ffmpeg_bin(), st.st_mode | stat.S_IEXEC)
    return ffmpeg_bin()


def ffmpeg_version_info():  # pragma: no cover
    """Get ffmpeg version."""
    try:
        r = subprocess.run([ffmpeg_bin(), "-version"], stdout=subprocess.PIPE)
        return (
            r.stdout.decode("utf-8")
            .strip()
            .splitlines()[0]
            .split()[2]
            .rstrip("-static")
            .rstrip("-tessu")
        )
    except FileNotFoundError:
        return "ffmpeg not installed"


def run_ffmpeg(args: list[str | Path]):
    """Run ffmpeg command with `args`. Install ffmpeg if not found."""
    cmd = [ffmpeg_bin()] + [str(a) for a in args]
    try:
        result = subprocess.run(cmd, capture_output=True, check=True)
    except FileNotFoundError:  # pragma: no cover
        print("FFMPEG not found - installing ...")
        ffmpeg_install()
        result = subprocess.run(cmd, capture_output=True, check=True)
    return result


def download_file(url, checksum):  # pragma: no cover
    # type: (str, str) -> str
    """Download file to app directory and return path to downloaded file."""
    url_obj = urlparse(url)
    if not url_obj.scheme == "https":
        raise ValueError("Only https connections supported.")
    file_name = os.path.basename(url_obj.path)
    out_dir = idk.dirs.user_data_dir
    out_path = os.path.join(out_dir, file_name)
    if os.path.exists(out_path):
        log.debug(f"{file_name} already exists. Checking integrity")
        b3_calc = blake3(open(out_path, "rb").read()).hexdigest()
        if not checksum == b3_calc:
            log.critical(f"Integrity error for {out_path}. Redownloading")
        else:
            log.debug(f"{file_name} integrity ok - skipping redownload")
            return out_path
    log.debug(f"downloading {url} to {out_path}")
    urlretrieve(url, filename=out_path)
    log.debug(f"verifying {out_path}")
    b3_calc = blake3(open(out_path, "rb").read()).hexdigest()
    if not checksum == b3_calc:
        raise RuntimeError(f"Failed integrity check for {out_path}")
    return out_path
