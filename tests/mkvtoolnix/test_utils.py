import os
from pathlib import Path

import pytest

from font_collector import MKVUtils

dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def test_is_mkv():
    assert MKVUtils.is_mkv(Path(os.path.join(dir_path, "file", "test video.mkv")))
    assert not MKVUtils.is_mkv(Path(os.path.join(dir_path, "file", "ass", "Style test.ass")))
    file_that_does_not_exist = Path(os.path.join(dir_path, "file", "file that does not exist"))
    with pytest.raises(FileNotFoundError) as exc_info:
        MKVUtils.is_mkv(file_that_does_not_exist)
    assert str(exc_info.value) == f'"{file_that_does_not_exist}" isn\'t a file or does not exist.'
