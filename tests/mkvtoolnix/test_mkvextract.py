import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from font_collector import MKVExtract

dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def test_get_mkv_font_files():
    if not MKVExtract.is_mkvextract_installed():
        assert False

    mkv_file = Path(os.path.join(dir_path, "file", "test video subs + 1 font.mkv"))

    with TemporaryDirectory() as tmp_dir:
        font_files = MKVExtract.get_mkv_font_files(mkv_file, Path(tmp_dir))

        assert len(font_files) == 2

        assert font_files[0].mkv_id == 1
        assert font_files[0].mkv_font_filename == "Cabin VF Beta Regular.ttf"
        assert font_files[0].filename.is_file()

        assert font_files[1].mkv_id == 2
        assert font_files[1].mkv_font_filename == "BELL.TTF"
        assert font_files[1].filename.is_file()

def test_get_mkv_ass_files():
    if not MKVExtract.is_mkvextract_installed():
        assert False

    mkv_file = Path(os.path.join(dir_path, "file", "test video subs + 1 font.mkv"))

    with TemporaryDirectory() as tmp_dir:
        ass_files = MKVExtract.get_mkv_ass_files(mkv_file, Path(tmp_dir))

        assert len(ass_files) == 1
        assert ass_files[0].mkv_id == 1
        assert ass_files[0].filename.is_file()
