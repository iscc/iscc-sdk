"""*Manage SDK binary media file handling tools*."""

import os
import platform
import shutil
import subprocess
import tarfile
import zipfile
from pathlib import Path
from platform import system, architecture
from typing import List
from urllib.parse import urlparse
from urllib.request import urlretrieve
from blake3 import blake3
from loguru import logger as log
import stat
import iscc_sdk as idk
from concurrent.futures import ThreadPoolExecutor


__all__ = [
    "install",
    "run_ffprobe",
    "run_ffmpeg",
    "run_fpcalc",
    "run_ipfs",
]

BASE_VERSION = "1.0.0"
BASE_URL = f"https://github.com/iscc/iscc-binaries/releases/download/v{BASE_VERSION}"

IPFS_VERSION = "0.12.0"
IPFS_URLS = {
    "windows-64": f"{BASE_URL}/go-ipfs_v{IPFS_VERSION}_windows-amd64.zip",
    "linux-64": f"{BASE_URL}/go-ipfs_v{IPFS_VERSION}_linux-amd64.tar.gz",
    "darwin-64": f"{BASE_URL}/go-ipfs_v{IPFS_VERSION}_darwin-amd64.tar.gz",
}
IPFS_CHECKSUMS = {
    "windows-64": "a2af645936a090c296b5d54755af0e9d6b1021f652195bb8fc596cf2073001c7",
    "linux-64": "7312b34bc7179c94c96e09a067b61d405672653bbaf70abee30396433a18ef81",
    "darwin-64": "3797fd0e6d5f922c095a12d860baccb49d90cef74accf49d219d4cea1b0d2bd7",
}

FFPROBE_VERSION = "6.1"
FFPROBE_URLS = {
    "windows-64": f"{BASE_URL}/ffprobe-{FFPROBE_VERSION}-win-64.zip",
    "linux-64": f"{BASE_URL}/ffprobe-{FFPROBE_VERSION}-linux-64.zip",
    "darwin-64": f"{BASE_URL}/ffprobe-{FFPROBE_VERSION}-macos-64.zip",
}
FFPROBE_CHECKSUMS = {
    "linux-64": "bd01b79f3a0d0a19cd0e086b38f60b4fad4d3274bb5cfebf8abc3f1da5603a16",
    "darwin-64": "799f36c0cd8797b015186e7aa78d1dd93a634f56e084325de2672d89a840eabb",
    "windows-64": "75497ab05dad5b8e7edb52ad1e1b626c8756fe33ae67825ab202b213f6d80548",
}

FFMPEG_VERSION = "6.1"
FFMPEG_URLS = {
    "windows-64": f"{BASE_URL}/ffmpeg-{FFMPEG_VERSION}-win-64.zip",
    "linux-64": f"{BASE_URL}/ffmpeg-{FFMPEG_VERSION}-linux-64.zip",
    "darwin-64": f"{BASE_URL}/ffmpeg-{FFMPEG_VERSION}-osx-64.zip",
}
FFMPEG_CHECKSUMS = {
    "linux-64": "e96b9796ad7404151eabaaaea30151fb9226554ee87d5164161fd20de4482dd1",
    "darwin-64": "ba9313f7bf8c46ebe60b8f39fa6de1657c94f51fd14d77c6e02ef09fab6ff5bc",
    "windows-64": "06814a07bff1f281a5282110ebff2ccb088cd9ffda35fce5af63b8e88cc2385a",
}

FPCALC_VERSION = "1.5.1"
FPCALC_URLS = {
    "windows-64": f"{BASE_URL}/chromaprint-fpcalc-{FPCALC_VERSION}-windows-x86_64.zip",
    "linux-64": f"{BASE_URL}/chromaprint-fpcalc-{FPCALC_VERSION}-linux-x86_64.tar.gz",
    "darwin-64": f"{BASE_URL}/chromaprint-fpcalc-{FPCALC_VERSION}-macos-x86_64.tar.gz",
}
FPCALC_CHECKSUMS = {
    "windows-64": "e29364a879ddf7bea403b0474a556e43f40d525e0d8d5adb81578f1fbf16d9ba",
    "linux-64": "190977d9419daed8a555240b9c6ddf6a12940c5ff470647095ee6242e217de5c",
    "darwin-64": "afea164b0bc9b91e5205d126f96a21836a91ea2d24200e1b7612a7304ea3b4f1",
}


def install():
    """Install binary tools for content extraction and metadata handling."""
    with ThreadPoolExecutor(max_workers=6) as p:
        p.submit(fpcalc_install)
        p.submit(ffprobe_install)
        p.submit(ffmpeg_install)
        p.submit(ipfs_install)
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
# IPFS                                                                                 #
########################################################################################


def ipfs_download_url() -> str:
    """Return system and version dependent IPFS download url."""
    return IPFS_URLS[system_tag()]


def ipfs_bin() -> str:
    """Returns local path to IPFS executable."""
    path = os.path.join(idk.dirs.user_data_dir, "go-ipfs", "ipfs")
    if system() == "Windows":
        path += ".exe"
    return path


def ipfs_download():  # pragma: no cover
    """Download IPFS and return path to archive file."""
    b3 = IPFS_CHECKSUMS.get(system_tag())
    return download_file(ipfs_download_url(), checksum=b3)


def ipfs_install():  # pragma: no cover
    """Install IPFS cli tool and return path to executble"""
    if is_installed(ipfs_bin()):
        log.debug("ipfs is already installed")
        return ipfs_bin()
    log.critical("installing ipfs")
    archive_path = ipfs_download()
    extract(archive_path)
    st = os.stat(ipfs_bin())
    os.chmod(ipfs_bin(), st.st_mode | stat.S_IEXEC)
    # Initialize ipfs repo
    subprocess.run([ipfs_bin(), "init"])
    return ipfs_bin()


def ipfs_version_info():  # pragma: no cover
    """Get IPFS version"""
    try:
        r = subprocess.run([ipfs_bin(), "--version"], stdout=subprocess.PIPE)
        return r.stdout.decode("utf-8").splitlines()[0].strip()
    except FileNotFoundError:
        return "IPFS not installed"


def run_ipfs(args: List[str]):
    """Run ipfs command with `args`. Install ipfs if not found."""
    cmd = [ipfs_bin()] + args
    try:
        result = subprocess.run(cmd, capture_output=True, check=True)
    except FileNotFoundError:  # pragma: no cover
        print("IPFS not found - installing ...")
        ipfs_install()
        result = subprocess.run(cmd, capture_output=True, check=True)
    return result


########################################################################################
# Fpcalc                                                                               #
########################################################################################


def fpcalc_bin():  # pragma: no cover
    """Returns local path to fpcalc executable."""
    if system() == "Windows":
        return os.path.join(idk.dirs.user_data_dir, "fpcalc-{}.exe".format(FPCALC_VERSION))
    return os.path.join(idk.dirs.user_data_dir, "fpcalc-{}".format(FPCALC_VERSION))


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


def run_fpcalc(args: List[str]):
    """Run fpcalc command with `args`. Installs fpcalc if not found."""
    cmd = [fpcalc_bin()] + args
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
    path = os.path.join(idk.dirs.user_data_dir, "ffprobe-{}".format(FFPROBE_VERSION))
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


def run_ffprobe(args: List[str]):  # pragma: no cover
    """Run ffprobe command with `args`. Install ffprobe if not found."""
    cmd = [ffprobe_bin()] + args
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
    path = os.path.join(idk.dirs.user_data_dir, "ffmpeg-{}".format(FFMPEG_VERSION))
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


def run_ffmpeg(args: List[str]):
    """Run ffmpeg command with `args`. Install ffmpeg if not found."""
    cmd = [ffmpeg_bin()] + args
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
