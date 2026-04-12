# -*- coding: utf-8 -*-
import time
from email.message import Message
from unittest.mock import patch, MagicMock
import iscc_sdk as idk
from iscc_sdk.utils import _filename_from_url


def test_tempfile(jpg_file):
    with idk.TempFile(jpg_file) as tf:
        assert tf.exists()
    assert not tf.exists()


def test_timer_measures_time():
    with patch("time.perf_counter") as mock_time:
        # Setup mock to return different values on each call
        mock_time.side_effect = [1.0, 2.5]  # Start time, end time
        with idk.timer("Test operation"):
            pass
    # Should have called perf_counter twice
    assert mock_time.call_count == 2


def test_timer_logs_message():
    with patch("time.perf_counter") as mock_time:
        mock_time.side_effect = [0.0, 1.5]
        with patch("loguru.logger.debug") as mock_log:
            with idk.timer("Test operation"):
                pass
            mock_log.assert_called_once_with("Test operation 1.5000 seconds")


def test_timer_with_exception():
    with patch("time.perf_counter") as mock_time:
        mock_time.side_effect = [0.0, 1.0]
        with patch("loguru.logger.debug") as mock_log:
            try:
                with idk.timer("Test operation"):
                    raise ValueError("Test error")
            except ValueError:
                pass
            # Should still log the timing even if an exception occurs
            mock_log.assert_called_once_with("Test operation 1.0000 seconds")


def test_timer_real_timing():
    with idk.timer("Sleep test"):
        time.sleep(0.1)  # Sleep for 100ms


def test_is_installed_true():
    assert idk.is_installed("iscc_schema") is True


def test_is_installed_false():
    assert idk.is_installed("non_existent_package") is False


def test_is_url_https():
    assert idk.is_url("https://example.com/file.pdf") is True


def test_is_url_http():
    assert idk.is_url("http://example.com/file.pdf") is True


def test_is_url_ftp():
    assert idk.is_url("ftp://example.com/file.pdf") is False


def test_is_url_local_path():
    assert idk.is_url("/some/local/file.pdf") is False


def test_is_url_windows_path():
    assert idk.is_url("C:\\Users\\file.pdf") is False


def test_is_url_relative_path():
    assert idk.is_url("relative/path.pdf") is False


def test_is_url_unparseable():
    with patch("iscc_sdk.utils.urlparse", side_effect=ValueError("bad url")):
        assert idk.is_url("anything") is False


def test_filename_from_url_simple():
    assert _filename_from_url("https://example.com/document.pdf") == "document.pdf"


def test_filename_from_url_nested_path():
    assert _filename_from_url("https://example.com/path/to/image.jpg") == "image.jpg"


def test_filename_from_url_with_query():
    assert _filename_from_url("https://example.com/doc.pdf?v=1&w=2") == "doc.pdf"


def test_filename_from_url_no_filename():
    assert _filename_from_url("https://example.com/") == "download"


def test_filename_from_url_content_disposition():
    headers = Message()
    headers["Content-Disposition"] = 'attachment; filename="report.pdf"'
    assert _filename_from_url("https://example.com/download", headers=headers) == "report.pdf"


def test_filename_from_url_content_disposition_no_quotes():
    headers = Message()
    headers["Content-Disposition"] = "attachment; filename=report.pdf"
    assert _filename_from_url("https://example.com/download", headers=headers) == "report.pdf"


def test_filename_from_url_content_disposition_with_spaces():
    headers = Message()
    headers["Content-Disposition"] = 'attachment; filename="my deck.pptx"'
    assert _filename_from_url("https://example.com/download", headers=headers) == "my deck.pptx"


def test_filename_from_url_path_traversal():
    headers = Message()
    headers["Content-Disposition"] = 'attachment; filename="../../etc/passwd"'
    assert _filename_from_url("https://example.com/download", headers=headers) == "passwd"


def test_filename_from_url_absolute_path():
    headers = Message()
    headers["Content-Disposition"] = 'attachment; filename="/etc/shadow"'
    assert _filename_from_url("https://example.com/download", headers=headers) == "shadow"


def test_download_file(jpg_file):
    """Test DownloadFile with mocked urlopen."""
    # Read test file content
    with open(jpg_file, "rb") as f:
        content = f.read()

    mock_response = MagicMock()
    mock_response.read = MagicMock(side_effect=[content, b""])
    mock_response.headers = Message()
    mock_response.geturl = MagicMock(return_value="https://example.com/img.jpg")
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=False)

    with patch("iscc_sdk.utils.urlopen", return_value=mock_response):
        with idk.DownloadFile("https://example.com/img.jpg") as tmp:
            assert tmp.exists()
            assert tmp.name == "img.jpg"
            with open(tmp, "rb") as f:
                assert f.read() == content
        # Temp file cleaned up
        assert not tmp.exists()


def test_download_file_cleanup_on_error(jpg_file):
    """Test that temp dir is cleaned up even if processing raises."""
    with open(jpg_file, "rb") as f:
        content = f.read()

    mock_response = MagicMock()
    mock_response.read = MagicMock(side_effect=[content, b""])
    mock_response.headers = Message()
    mock_response.geturl = MagicMock(return_value="https://example.com/img.jpg")
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=False)

    with patch("iscc_sdk.utils.urlopen", return_value=mock_response):
        try:
            with idk.DownloadFile("https://example.com/img.jpg") as tmp:
                saved_path = tmp
                raise ValueError("simulated error")
        except ValueError:
            pass
        assert not saved_path.exists()
