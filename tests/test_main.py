import json
import os
import pytest
import shutil
import subprocess
from pathlib import Path
from font_collector import Mkvpropedit, FontFile

dir_path = os.path.dirname(os.path.realpath(__file__))



def test_main():
    font_filename = Path(os.path.join(dir_path, "font_mac.TTF"))
    output_dir = os.path.join(dir_path)

    assert not font_filename.is_file()

    cmd = [
        "fontcollector",
        "-i", os.path.join(dir_path, "file", "ass", "sample.ass"),
        "--additional-fonts", os.path.join(dir_path, "file", "fonts", "font_mac.TTF"),
        "-o", output_dir,
        "--exclude-system-fonts"
    ]

    output = subprocess.run(cmd)
    assert output.returncode == 0
    assert font_filename.is_file()

    os.remove(font_filename)
