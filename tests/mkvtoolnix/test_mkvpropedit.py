import os
import shutil
from pathlib import Path

from font_collector import FontFile, MKVMerge, MKVPropedit

dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def test_delete_all_fonts_of_mkv():
    if not MKVMerge.is_mkvmerge_installed():
        assert False

    original_mkv_file = Path(os.path.join(dir_path, "file", "test video.mkv"))
    temp_mkv_file = Path(os.path.join(dir_path, "file", "test_video_temp.mkv"))
    shutil.copy(original_mkv_file, temp_mkv_file)
    font_cmap_encoding_0 = Path(os.path.join(dir_path, "file", "fonts", "font_cmap_encoding_0.ttf"))
    font_file = FontFile.from_font_path(font_cmap_encoding_0)

    # Get the video detail
    mkvmerge_output_dict = MKVMerge.get_mkv_info(temp_mkv_file)

    if len(mkvmerge_output_dict["attachments"]) != 0:
        raise ValueError(f'The video "{original_mkv_file} need to have 0 attachments"')

    # Verify if the font have been merged
    MKVPropedit.merge_fonts_into_mkv([font_file], temp_mkv_file)
    mkvmerge_output_dict = MKVMerge.get_mkv_info(temp_mkv_file)

    assert len(mkvmerge_output_dict["attachments"]) == 1
    assert mkvmerge_output_dict["attachments"][0]["file_name"] == font_file.filename.resolve().name

    # Verify if the font have been deleted
    MKVPropedit.delete_all_fonts_of_mkv(temp_mkv_file)
    mkvmerge_output_dict = MKVMerge.get_mkv_info(temp_mkv_file)

    assert len(mkvmerge_output_dict["attachments"]) == 0

    os.remove(temp_mkv_file)

def test_delete_fonts_of_mkv():
    if not MKVMerge.is_mkvmerge_installed():
        assert False

    original_mkv_file = Path(os.path.join(dir_path, "file", "test video subs + 1 font.mkv"))
    temp_mkv_file = Path(os.path.join(dir_path, "file", "test video subs + 1 font temp.mkv"))
    shutil.copy(original_mkv_file, temp_mkv_file)

    mkv_info = MKVMerge.get_mkv_info(temp_mkv_file)
    assert len(mkv_info["attachments"]) == 2

    MKVPropedit.delete_fonts_of_mkv(temp_mkv_file, [1])

    mkv_info = MKVMerge.get_mkv_info(temp_mkv_file)
    assert len(mkv_info["attachments"]) == 1

    os.remove(temp_mkv_file)

def test_merge_fonts_into_mkv():
    if not MKVMerge.is_mkvmerge_installed():
        assert False

    original_mkv_file = Path(os.path.join(dir_path, "file", "test video.mkv"))
    temp_mkv_file = Path(os.path.join(dir_path, "file", "test_video_temp_1.mkv"))
    shutil.copy(original_mkv_file, temp_mkv_file)
    font_cmap_encoding_0 = Path(os.path.join(dir_path, "file", "fonts", "font_cmap_encoding_0.ttf"))
    font_file = FontFile.from_font_path(font_cmap_encoding_0)

    # Get the video detail
    mkvmerge_output_dict = MKVMerge.get_mkv_info(temp_mkv_file)

    if len(mkvmerge_output_dict["attachments"]) != 0:
        raise ValueError(f'The video "{original_mkv_file} need to have 0 attachments"')

    # Verify if the font have been merged
    MKVPropedit.merge_fonts_into_mkv([font_file], temp_mkv_file)
    mkvmerge_output_dict = MKVMerge.get_mkv_info(temp_mkv_file)

    assert len(mkvmerge_output_dict["attachments"]) == 1
    assert mkvmerge_output_dict["attachments"][0]["file_name"] == font_file.filename.resolve().name

    os.remove(temp_mkv_file)
