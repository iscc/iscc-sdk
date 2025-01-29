# -*- coding: utf-8 -*-
import time
from unittest.mock import patch
import iscc_sdk as idk


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
