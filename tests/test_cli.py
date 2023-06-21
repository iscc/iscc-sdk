import pytest
import sys
from pathlib import Path
from typing import Tuple
from typer.testing import CliRunner
from iscc_sdk.cli import app, iter_unprocessed, process_file
import iscc_samples as iss
import json


runner = CliRunner()


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
    assert result.exit_code == 0
    assert "Usage" in result.stdout


def test_cli_create_no_arg():
    result = runner.invoke(app, ["create"])
    assert result.exit_code == 2
    assert "Missing argument 'FILE'" in result.stdout


def test_cli_create_not_file():
    result = runner.invoke(app, ["create", "not-a-file"])
    assert result.exit_code == 1
    assert "Invalid file path" in result.stdout


def test_cli_create():
    result = runner.invoke(app, ["create", iss.audios(ext="mp3")[0].as_posix()])
    assert result.exit_code == 0
    assert json.loads(result.stdout) == {
        "@context": "http://purl.org/iscc/context/0.4.0.jsonld",
        "$schema": "http://purl.org/iscc/schema/0.4.0.json",
        "@type": "AudioObject",
        "iscc": "ISCC:KIC2JKSX7OH5PBIENISKEJTS4TRKHYJBCZDNLQXYILWJHQAP3N3KPTQ",
        "name": "Belly Button",
        "mode": "audio",
        "filename": "demo.mp3",
        "filesize": 225707,
        "mediatype": "audio/mpeg",
        "duration": 15,
        "metahash": "1e20c4933dc8c03ea58568159a1cbfb04132c7db93b6b4cd025ffd4db37f52a4756f",
        "datahash": "1e20ec93c00fdb76a7cec587e4a2bddfa8d0a0bac8110d0c7130c351ea07c366d626",
    }


def test_cli_batch_no_arg():
    result = runner.invoke(app, ["batch"])
    assert result.exit_code == 2
    assert "Missing argument 'FOLDER'" in result.stdout


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
