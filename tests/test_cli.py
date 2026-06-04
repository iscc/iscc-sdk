import pytest
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Tuple
from typer.testing import CliRunner
from iscc_sdk.cli import app, iter_unprocessed, process_file
import iscc_schema
import iscc_samples as iss
import json


runner = CliRunner()

# iscc-schema stamps its own version into the @context and $schema URLs.
SCHEMA_VERSION = iscc_schema.__version__


def test_iter_unprocessed():
    files = list(iter_unprocessed(iss.audios()[0].parent))
    assert isinstance(files[0], Tuple)
    assert isinstance(files[0][0], Path)
    assert isinstance(files[0][1], int)
    assert len(files) == 10


def test_process_file(jpg_file):
    fp, iscc_meta = process_file(Path(jpg_file))
    assert fp == Path(jpg_file)
    assert iscc_meta.iscc == "ISCC:KECWRY3VY6R5SNV4YNBTBHR4T2HGP3HKVFO7TYUP2BKVFG724W63HVI"


def test_process_file_error():
    fp, iscc_meta = process_file(Path("does-not-exist"))
    assert fp == Path("does-not-exist")
    assert isinstance(iscc_meta, Exception)


def test_cli_no_arg():
    result = runner.invoke(app)
    assert result.exit_code == 2
    assert "Usage" in result.stdout


def test_cli_create_no_arg():
    result = runner.invoke(app, ["create"])
    assert result.exit_code == 2
    assert "Missing argument 'FILE'" in result.stderr


def test_cli_create_not_file():
    result = runner.invoke(app, ["create", "not-a-file"])
    assert result.exit_code == 1
    assert "Invalid file path" in result.stdout


def test_cli_create():
    result = runner.invoke(app, ["create", iss.audios(ext="mp3")[0].as_posix()])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert "iscc-sdk" in data["generator"]
    del data["generator"]
    assert data == {
        "@context": f"http://purl.org/iscc/context/{SCHEMA_VERSION}.jsonld",
        "$schema": f"http://purl.org/iscc/schema/{SCHEMA_VERSION}.json",
        "@type": "AudioObject",
        "iscc": "ISCC:KIC2JKSX7OH5PBIENISKEJTS4TRKHYJBCZDNLQXYILWJHQAP3N3KPTQ",
        "name": "Belly Button",
        "mode": "audio",
        "filename": "demo.mp3",
        "filesize": 225707,
        "mediatype": "audio/mpeg",
        "duration": 16,
        "metahash": "1e20c4933dc8c03ea58568159a1cbfb04132c7db93b6b4cd025ffd4db37f52a4756f",
        "datahash": "1e20ec93c00fdb76a7cec587e4a2bddfa8d0a0bac8110d0c7130c351ea07c366d626",
    }


def test_cli_create_svg(svg_file):
    result = runner.invoke(app, ["create", svg_file])
    assert result.exit_code == 0
    assert "ISCC:" in result.stdout


def test_cli_create_unsupported(dat_file):
    result = runner.invoke(app, ["create", dat_file])
    assert result.exit_code == 1
    assert "No known processing mode for" in result.stdout


def test_cli_batch_no_arg():
    result = runner.invoke(app, ["batch"])
    assert result.exit_code == 2
    assert "Missing argument 'FOLDER'" in result.stderr


def test_cli_batch_not_a_folder():
    result = runner.invoke(app, ["batch", "not-a-folder"])
    assert result.exit_code == 1
    assert "Invalid folder" in result.stdout


@pytest.mark.skipif(sys.platform == "linux", reason="To be investigated")
def test_cli_batch(asset_tree):
    result = runner.invoke(app, ["batch", asset_tree.as_posix()])
    assert result.exit_code == 0
    assert list(iter_unprocessed(asset_tree)) == []


def test_cli_selftest():
    result = runner.invoke(app, ["selftest"])
    assert result.exit_code == 0


def test_cli_install():
    result = runner.invoke(app, ["install"])
    assert result.exit_code == 0


def test_cli_extract_no_arg():
    result = runner.invoke(app, ["extract"])
    assert result.exit_code == 2
    assert "Missing argument 'FILE'" in result.stderr


def test_cli_extract_not_file():
    result = runner.invoke(app, ["extract", "not-a-file"])
    assert result.exit_code == 1
    assert "Invalid file path" in result.stdout


def test_cli_extract():
    result = runner.invoke(app, ["extract", iss.texts()[0].as_posix()])
    assert result.exit_code == 0
    assert "lorem ipsum" in result.stdout.lower()


def test_cli_extract_error(monkeypatch):
    def mock_text_extract(*args, **kwargs):
        raise Exception("Test extraction error")

    monkeypatch.setattr("iscc_sdk.text_extract", mock_text_extract)

    # Use a real file that exists but will trigger our mocked exception
    result = runner.invoke(app, ["extract", iss.texts()[0].as_posix()])
    assert result.exit_code == 1
    assert "Error extracting text: Test extraction error" in result.stdout


def test_cli_create_url(monkeypatch):
    """Test create command with a URL input."""
    audio_path = iss.audios(ext="mp3")[0]

    @contextmanager
    def mock_download(url):
        yield audio_path

    monkeypatch.setattr("iscc_sdk.cli.idk.DownloadFile", mock_download)
    result = runner.invoke(app, ["create", "https://example.com/demo.mp3"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert "ISCC:" in data["iscc"]


def test_cli_create_url_download_error(monkeypatch):
    """Test create command with a URL that fails to download."""

    @contextmanager
    def mock_download(url):
        raise ConnectionError("Network unreachable")
        yield  # pragma: no cover

    monkeypatch.setattr("iscc_sdk.cli.idk.DownloadFile", mock_download)
    result = runner.invoke(app, ["create", "https://example.com/file.pdf"])
    assert result.exit_code == 1
    assert "Error downloading or processing URL" in result.stdout


def test_cli_create_url_unsupported(monkeypatch, dat_file):
    """Test create command with a URL pointing to unsupported media type."""

    @contextmanager
    def mock_download(url):
        yield Path(dat_file)

    monkeypatch.setattr("iscc_sdk.cli.idk.DownloadFile", mock_download)
    result = runner.invoke(app, ["create", "https://example.com/data.dat"])
    assert result.exit_code == 1
    assert "No known processing mode for" in result.stdout


def test_cli_extract_url(monkeypatch):
    """Test extract command with a URL input."""
    text_path = iss.texts()[0]

    @contextmanager
    def mock_download(url):
        yield text_path

    monkeypatch.setattr("iscc_sdk.cli.idk.DownloadFile", mock_download)
    result = runner.invoke(app, ["extract", "https://example.com/text.txt"])
    assert result.exit_code == 0
    assert len(result.stdout.strip()) > 0


def test_cli_extract_url_error(monkeypatch):
    """Test extract command with a URL that fails."""

    @contextmanager
    def mock_download(url):
        raise ConnectionError("Network unreachable")
        yield  # pragma: no cover

    monkeypatch.setattr("iscc_sdk.cli.idk.DownloadFile", mock_download)
    result = runner.invoke(app, ["extract", "https://example.com/file.pdf"])
    assert result.exit_code == 1
    assert "Error downloading or extracting text" in result.stdout
