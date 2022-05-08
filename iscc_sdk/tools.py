"""*SDK binary media file handling tools*."""
import os
import shutil
import subprocess
import sys
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
import jdk
import iscc_sdk as idk
from concurrent.futures import ThreadPoolExecutor


__all__ = [
    "install",
    "run_ffmpeg",
    "run_fpcalc",
    "run_exiv2",
    "run_exiv2json",
    "run_ipfs",
    "run_tika",
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

FFMPEG_VERSION = "4.4.1"
FFMPEG_URLS = {
    "windows-64": f"{BASE_URL}/ffmpeg-{FFMPEG_VERSION}-win-64.zip",
    "linux-64": f"{BASE_URL}/ffmpeg-{FFMPEG_VERSION}-linux-64.zip",
    "darwin-64": f"{BASE_URL}/ffmpeg-{FFMPEG_VERSION}-osx-64.zip",
}
FFMPEG_CHECKSUMS = {
    "windows-64": "b77405ee98580971cb36c4ca0c7f888283dcffc347c282b304abbb3c1eee6fc2",
    "linux-64": "a8ac9f1e28ad31ca366dba17dd0c486926d533d76ffc9b47a976308245ab064e",
    "darwin-64": "33f980b5b59ddfc663170a419110e9504527c092b21ba6592c525f7a7c183887",
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

TIKA_VERSION = "2.3.0"
TIKA_URL = f"{BASE_URL}/tika-app-{TIKA_VERSION}.jar"
TIKA_CHECKSUM = "e3f6ff0841b9014333fc6de4b849704384abf362100edfa573a6e4104b654491"

EXIV2_VERSION = "0.27.2"
EXIV2_URLS = {
    "windows-64": f"{BASE_URL}/exiv2-{EXIV2_VERSION}-2017msvc64.zip",
    "linux-64": f"{BASE_URL}/exiv2-{EXIV2_VERSION}-Linux64.tar.gz",
    "darwin-64": f"{BASE_URL}/exiv2-{EXIV2_VERSION}-Darwin.tar.gz",
}

EXIV2_CHECKSUMS = {
    "windows-64": "63eef38590c7d777d75d2f8384fdfb03d47b1226c5f0bff066d97dcaacff8998",
    "linux-64": "77cc0200c13a4c7d42363cddc76befdf8b8a19225bf48f8bcce8914d12cb1eae",
    "darwin-64": "f81a99689507de4c177aeb0a93c1442962619747184b91b9498cbd78242695d1",
}

EXIV2_RELPATH = {
    "windows-64": f"exiv2-{EXIV2_VERSION}-2017msvc64/bin/exiv2.exe",
    "linux-64": f"exiv2-{EXIV2_VERSION}-Linux64/bin/exiv2",
    "darwin-64": f"exiv2-{EXIV2_VERSION}-Darwin/bin/exiv2",
}

EXIV2JSON_RELPATH = {
    "windows-64": f"exiv2-{EXIV2_VERSION}-2017msvc64/bin/exiv2json.exe",
    "linux-64": f"exiv2-{EXIV2_VERSION}-Linux64/bin/exiv2json",
    "darwin-64": f"exiv2-{EXIV2_VERSION}-Darwin/bin/exiv2json",
}


def install():
    """Install binary tools for content extraction."""
    with ThreadPoolExecutor(max_workers=6) as p:
        p.submit(exiv2_install)
        p.submit(fpcalc_install)
        p.submit(ffmpeg_install)
        p.submit(tika_install)
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
            tar_file.extractall(Path(archive).parent.absolute())
    os.unlink(archive)


########################################################################################
# IPFS                                                                                 #
########################################################################################


def ipfs_download_url() -> str:
    """Return system and version dependant IPFS download url."""
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
    cmd = [ipfs_bin()] + args
    try:
        result = subprocess.run(cmd, capture_output=True, check=True)
    except FileNotFoundError:  # pragma: no cover
        print("IPFS not found - installing ...")
        ipfs_install()
        result = subprocess.run(cmd, capture_output=True, check=True)
    return result


########################################################################################
# Exiv2                                                                                #
########################################################################################


def exiv2_download_url() -> str:
    """Return system and version dependant exiv2 download url."""
    return EXIV2_URLS[system_tag()]


def exiv2_bin() -> str:
    """Returns local path to exiv2 executable."""
    return os.path.join(idk.dirs.user_data_dir, EXIV2_RELPATH[system_tag()])


def exiv2json_bin() -> str:
    return os.path.join(idk.dirs.user_data_dir, EXIV2JSON_RELPATH[system_tag()])


def exiv2_is_installed():  # pragma: no cover
    """Check if exiv2 is installed."""
    fp = exiv2_bin()
    return os.path.isfile(fp) and os.access(fp, os.X_OK)


def exiv2_download():  # pragma: no cover
    b3 = EXIV2_CHECKSUMS[system_tag()]
    return download_file(exiv2_download_url(), checksum=b3)


def exiv2_install():  # pragma: no cover
    """Install exiv2 command line tool and return path to executable."""
    if exiv2_is_installed():
        log.debug("Exiv2 is already installed.")
        return exiv2_bin()
    log.critical("installing exiv2")
    archive_path = exiv2_download()
    extract(archive_path)
    st = os.stat(exiv2_bin())
    os.chmod(exiv2_bin(), st.st_mode | stat.S_IEXEC)
    st = os.stat(exiv2json_bin())
    os.chmod(exiv2json_bin(), st.st_mode | stat.S_IEXEC)

    # macOS workaround to avoid dynamic linking issues
    # Correct way would be to set DYLD_LIBRARY_PATH when calling exiv2,
    # but this makes it easier.
    if system().lower() == "darwin":
        lib_path = Path(exiv2_bin()).parent / ".." / "lib" / "libexiv2.27.dylib"
        lib_bin_path = Path(exiv2_bin()).parent / "libexiv2.27.dylib"
        os.symlink(lib_path, lib_bin_path)

    return exiv2_bin()


def exiv2_version_info():  # pragma: no cover
    """Get exiv2 version info."""
    try:
        r = subprocess.run(
            [exiv2_bin(), "--version"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        vi = r.stdout.decode(sys.stdout.encoding)
        return vi.splitlines()[0]
    except FileNotFoundError:
        return "exiv2 not installed"


def run_exiv2(args: List[str]):
    cmd = [exiv2_bin()] + args
    try:
        result = subprocess.run(cmd, capture_output=True, check=True)
    except FileNotFoundError:  # pragma: no cover
        print("EXIV2 not found - installing ...")
        exiv2_install()
        result = subprocess.run(cmd, capture_output=True, check=True)
    return result


def run_exiv2json(args: List[str]):
    cmd = [exiv2json_bin()] + args
    try:
        result = subprocess.run(cmd, capture_output=True, check=True)
    except FileNotFoundError:  # pragma: no cover
        print("EXIV2 not found - installing ...")
        exiv2_install()
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
    """Return system and version dependant download url."""
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
    cmd = [fpcalc_bin()] + args
    try:
        result = subprocess.run(cmd, capture_output=True, check=True)
    except FileNotFoundError:  # pragma: no cover
        print("FPCALC not found - installing ...")
        fpcalc_install()
        result = subprocess.run(cmd, capture_output=True, check=True)
    return result


########################################################################################
# ffmpeg                                                                               #
########################################################################################


def ffmpeg_download_url():
    """Return system dependant download url."""
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
    """Run ffmpeg command with `args`"""
    cmd = [ffmpeg_bin()] + args
    try:
        result = subprocess.run(cmd, capture_output=True, check=True)
    except FileNotFoundError:  # pragma: no cover
        print("FFMPEG not found - installing ...")
        ffmpeg_install()
        result = subprocess.run(cmd, capture_output=True, check=True)
    return result


########################################################################################
# Java                                                                                 #
########################################################################################


def java_bin():  # pragma: no cover
    java_path = shutil.which("java")
    if not java_path:
        java_path = java_custom_path()
    return java_path


def java_custom_path():  # pragma: no cover
    if system() == "Windows":
        java_path = os.path.join(idk.dirs.user_data_dir, "jdk-16.0.2+7-jre", "bin", "java.exe")
    else:
        java_path = os.path.join(idk.dirs.user_data_dir, "jdk-16.0.2+7-jre", "bin", "java")
    return java_path


def java_is_installed():  # pragma: no cover
    return bool(shutil.which("java")) or is_installed(java_custom_path())


def java_install():  # pragma: no cover
    if java_is_installed():
        log.debug("java already installed")
        return java_bin()
    log.critical("installing java")
    return jdk.install("16", impl="openj9", jre=True, path=idk.dirs.user_data_dir)


def java_version_info():  # pragma: no cover
    try:
        r = subprocess.run([java_bin(), "-version"], stderr=subprocess.PIPE)
        return r.stderr.decode(sys.stdout.encoding).splitlines()[0]
    except subprocess.CalledProcessError:
        return "JAVA not installed"


########################################################################################
# Apache Tika                                                                          #
########################################################################################


def tika_download_url():
    # type: () -> str
    """Return tika download url."""
    return TIKA_URL


def tika_bin():
    # type: () -> str
    """Returns path to java tika app call."""
    return os.path.join(idk.dirs.user_data_dir, f"tika-app-{TIKA_VERSION}.jar")


def tika_is_installed():  # pragma: no cover
    # type: () -> bool
    """Check if tika is installed."""
    return os.path.exists(tika_bin())


def tika_download():  # pragma: no cover
    # type: () -> str
    """Download tika-app.jar and return local path."""
    return download_file(tika_download_url(), checksum=TIKA_CHECKSUM)


def tika_install():  # pragma: no cover
    # type: () -> str
    """Install tika-app.jar if not installed yet."""
    # Ensure JAVA is installed
    java_install()

    if tika_is_installed():
        log.debug("Tika is already installed")
        return tika_bin()
    else:
        log.critical("installing tika")
        path = tika_download()
        st = os.stat(tika_bin())
        os.chmod(tika_bin(), st.st_mode | stat.S_IEXEC)
        return path


def tika_version_info():  # pragma: no cover
    # type: () -> str
    """
    Check tika-app version.

    :return: Tika version info string
    :rtype: str
    """
    try:
        r = subprocess.run([java_bin(), "-jar", tika_bin(), "--version"], stdout=subprocess.PIPE)
        return r.stdout.decode(sys.stdout.encoding).strip()
    except subprocess.CalledProcessError:
        return "Tika not installed"


def run_tika(args: List[str]):
    cmd = [java_bin(), "-jar", tika_bin()] + args
    try:
        result = subprocess.run(cmd, capture_output=True, check=True)
    except Exception as e:  # pragma: no cover
        print(f"TIKA error - {e}")
        print(f"Re-Installing TIKA ...")
        tika_install()
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
