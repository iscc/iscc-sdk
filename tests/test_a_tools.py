# -*- coding: utf-8 -*-
import os
from iscc_sdk import tools


def test_install():
    assert tools.install() is True


def test_system_tag():
    assert "64" in tools.system_tag()


def test_is_installed():
    assert tools.is_installed(tools.ffmpeg_bin())


def test_exiv2_download_url():
    assert "exiv" in tools.exiv2_download_url()


def test_exiv2_bin():
    bpath = tools.exiv2_bin()
    assert os.path.basename(bpath).startswith("exiv2")


def test_exiv2json_bin():
    assert "exiv2" in tools.exiv2json_bin()


def test_fpcalc_downlod_url():
    assert "fpcalc" in tools.fpcalc_download_url()


def test_ffmpeg_download_url():
    assert "ffmpeg" in tools.ffmpeg_download_url()


def test_ffmpeg_bin():
    assert "ffmpeg" in tools.ffmpeg_bin()


def test_tika_download_url():
    assert "tika" in tools.tika_download_url()


def test_tika_bin():
    assert "tika" in tools.tika_bin()


def test_java_version_info():
    vi = tools.java_version_info().lower()
    assert "java" in vi or "openjdk" in vi
    assert len(vi.splitlines()) == 1


def test_tika_version_info():
    assert tools.TIKA_VERSION in tools.tika_version_info()


def test_ffmpeg_version_info():
    assert tools.FFMPEG_VERSION in tools.ffmpeg_version_info()


def test_fpcalc_version_info():
    assert tools.FPCALC_VERSION in tools.fpcalc_version_info()


def test_exiv2_version_info():
    assert "exiv2" in tools.exiv2_version_info().lower()


def test_ipfs_download_url():
    assert "ipfs" in tools.ipfs_download_url()


def test_ipfs_bin():
    assert os.path.exists(tools.ipfs_bin())


def test_ipfs_version_info():
    assert "ipfs version" in tools.ipfs_version_info()
