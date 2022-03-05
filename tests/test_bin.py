# -*- coding: utf-8 -*-
import os
from iscc_sdk import bin


def test_install():
    assert bin.install() is True


def test_system_tag():
    assert "64" in bin.system_tag()


def test_is_installed():
    assert bin.is_installed(bin.ffmpeg_bin())


def test_exiv2_download_url():
    assert "exiv" in bin.exiv2_download_url()


def test_exiv2_bin():
    bpath = bin.exiv2_bin()
    assert os.path.basename(bpath).startswith("exiv2")


def test_exiv2json_bin():
    assert "exiv2" in bin.exiv2json_bin()


def test_fpcalc_downlod_url():
    assert "fpcalc" in bin.fpcalc_download_url()


def test_ffprobe_download_url():
    assert "ffprobe" in bin.ffprobe_download_url()


def test_ffprobe_bin():
    assert "ffprobe" in bin.ffprobe_bin()


def test_ffmpeg_download_url():
    assert "ffmpeg" in bin.ffmpeg_download_url()


def test_ffmpeg_bin():
    assert "ffmpeg" in bin.ffmpeg_bin()


def test_tika_download_url():
    assert "tika" in bin.tika_download_url()


def test_tika_bin():
    assert "tika" in bin.tika_bin()


def test_java_version_info():
    vi = bin.java_version_info().lower()
    assert "java" in vi or "openjdk" in vi
    assert len(vi.splitlines()) == 1


def test_tika_version_info():
    assert bin.TIKA_VERSION in bin.tika_version_info()


def test_ffprobe_version_info():
    assert bin.FFPROBE_VERSION in bin.ffprobe_version_info()


def test_ffmpeg_version_info():
    assert bin.FFMPEG_VERSION in bin.ffmpeg_version_info()


def test_fpcalc_version_info():
    assert bin.FPCALC_VERSION in bin.fpcalc_version_info()


def test_exiv2_version_info():
    assert "exiv2" in bin.exiv2_version_info().lower()
