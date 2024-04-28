import json
import os
import pytest
import shutil
import subprocess
from pathlib import Path
from font_collector import Mkvpropedit, FontFile

dir_path = os.path.dirname(os.path.realpath(__file__))


def test_is_mkv():
    assert Mkvpropedit.is_mkv(Path(os.path.join(dir_path, "file", "test video.mkv")))
    assert not Mkvpropedit.is_mkv(Path(os.path.join(dir_path, "file", "ass", "Style test.ass")))
    file_that_does_not_exist = Path(os.path.join(dir_path, "file", "file that does not exist"))
    with pytest.raises(FileNotFoundError) as exc_info:
        Mkvpropedit.is_mkv(file_that_does_not_exist)
    assert str(exc_info.value) == f'The file "{file_that_does_not_exist}" does not exist.'

def test_delete_fonts_of_mkv():
    mkvmerge = shutil.which("mkvmerge")
    if mkvmerge is None:
        assert False

    original_mkv_file = Path(os.path.join(dir_path, "file", "test video.mkv"))
    temp_mkv_file = Path(os.path.join(dir_path, "file", "test_video_temp.mkv"))
    shutil.copy(original_mkv_file, temp_mkv_file)
    font_cmap_encoding_0 = Path(os.path.join(dir_path, "file", "fonts", "font_cmap_encoding_0.ttf"))
    font_file = FontFile.from_font_path(font_cmap_encoding_0)

    # Get the video detail
    cmd = [
        "mkvmerge",
        temp_mkv_file,
        "-J",
    ]
    mkvmerge_output = subprocess.run(cmd, capture_output=True, text=True)
    if mkvmerge_output.returncode == 2:
        raise ValueError(f"mkvmerge reported this error: {mkvmerge_output.stdout}")
    mkvmerge_output_dict = json.loads(mkvmerge_output.stdout)

    if len(mkvmerge_output_dict["attachments"]) != 0:
        raise ValueError(f'The video "{original_mkv_file} need to have 0 attachments"')

    # Verify if the font have been merged
    Mkvpropedit.merge_fonts_into_mkv([font_file], temp_mkv_file)
    cmd = [
        "mkvmerge",
        temp_mkv_file,
        "-J",
    ]
    mkvmerge_output = subprocess.run(cmd, capture_output=True, text=True)
    if mkvmerge_output.returncode == 2:
        raise ValueError(f"mkvmerge reported this error: {mkvmerge_output.stdout}")
    mkvmerge_output_dict = json.loads(mkvmerge_output.stdout)

    assert len(mkvmerge_output_dict["attachments"]) == 1
    assert mkvmerge_output_dict["attachments"][0]["file_name"] == font_file.filename.resolve().name

    # Verify if the font have been deleted
    Mkvpropedit.delete_fonts_of_mkv(temp_mkv_file)
    cmd = [
        "mkvmerge",
        temp_mkv_file,
        "-J",
    ]
    mkvmerge_output = subprocess.run(cmd, capture_output=True, text=True)
    if mkvmerge_output.returncode == 2:
        raise ValueError(f"mkvmerge reported this error: {mkvmerge_output.stdout}")
    mkvmerge_output_dict = json.loads(mkvmerge_output.stdout)

    assert len(mkvmerge_output_dict["attachments"]) == 0

    os.remove(temp_mkv_file)

def test_merge_fonts_into_mkv():
    mkvmerge = shutil.which("mkvmerge")
    if mkvmerge is None:
        assert False

    original_mkv_file = Path(os.path.join(dir_path, "file", "test video.mkv"))
    temp_mkv_file = Path(os.path.join(dir_path, "file", "test_video_temp_1.mkv"))
    shutil.copy(original_mkv_file, temp_mkv_file)
    font_cmap_encoding_0 = Path(os.path.join(dir_path, "file", "fonts", "font_cmap_encoding_0.ttf"))
    font_file = FontFile.from_font_path(font_cmap_encoding_0)

    # Get the video detail
    cmd = [
        "mkvmerge",
        temp_mkv_file,
        "-J",
    ]
    mkvmerge_output = subprocess.run(cmd, capture_output=True, text=True)
    if mkvmerge_output.returncode == 2:
        raise ValueError(f"mkvmerge reported this error: {mkvmerge_output.stdout}")
    mkvmerge_output_dict = json.loads(mkvmerge_output.stdout)

    if len(mkvmerge_output_dict["attachments"]) != 0:
        raise ValueError(f'The video "{original_mkv_file} need to have 0 attachments"')

    # Verify if the font have been merged
    Mkvpropedit.merge_fonts_into_mkv([font_file], temp_mkv_file)
    cmd = [
        "mkvmerge",
        temp_mkv_file,
        "-J",
    ]
    mkvmerge_output = subprocess.run(cmd, capture_output=True, text=True)
    if mkvmerge_output.returncode == 2:
        raise ValueError(f"mkvmerge reported this error: {mkvmerge_output.stdout}")
    mkvmerge_output_dict = json.loads(mkvmerge_output.stdout)

    assert len(mkvmerge_output_dict["attachments"]) == 1
    assert mkvmerge_output_dict["attachments"][0]["file_name"] == font_file.filename.resolve().name

    os.remove(temp_mkv_file)
