# -*- coding: utf-8 -*-
import os
from iscc_sdk import tools


def test_install():
    assert tools.install() is True


def test_system_tag():
    assert "64" in tools.system_tag()


def test_is_installed():
    assert tools.is_installed(tools.ffmpeg_bin())


def test_fpcalc_downlod_url():
    assert "fpcalc" in tools.fpcalc_download_url()


def test_ffprobe_download_url():
    assert "ffprobe" in tools.ffprobe_download_url()


def test_ffprobe_bin():
    assert "ffprobe" in tools.ffprobe_bin()


def test_ffmpeg_download_url():
    assert "ffmpeg" in tools.ffmpeg_download_url()


def test_ffmpeg_bin():
    assert "ffmpeg" in tools.ffmpeg_bin()


def test_ffprobe_version_info():
    assert tools.FFPROBE_VERSION in tools.ffprobe_version_info()


def test_ffmpeg_version_info():
    assert tools.FFMPEG_VERSION in tools.ffmpeg_version_info()


def test_fpcalc_version_info():
    assert tools.FPCALC_VERSION in tools.fpcalc_version_info()


def test_ipfs_download_url():
    assert "ipfs" in tools.ipfs_download_url()


def test_ipfs_bin():
    assert os.path.exists(tools.ipfs_bin())


def test_ipfs_version_info():
    assert "ipfs version" in tools.ipfs_version_info()
