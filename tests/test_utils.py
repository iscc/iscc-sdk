# -*- coding: utf-8 -*-
import iscc_sdk as idk


def test_tempfile(jpg_file):
    with idk.TempFile(jpg_file) as tf:
        assert tf.exists()
    assert not tf.exists()
