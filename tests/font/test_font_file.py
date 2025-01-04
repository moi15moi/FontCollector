import os
import shutil
from collections.abc import Hashable
from pathlib import Path
from time import time

import pytest
from langcodes import Language

from font_collector import (
    FontFile,
    FontType,
    Name,
    NormalFontFace,
    VariableFontFace
)

dir_path = os.path.dirname(os.path.realpath(__file__))
filename = Path(os.path.join(os.path.dirname(dir_path), "file", "fonts", "Asap-VariableFont_wdth,wght.ttf"))

def test__init__():
    font_faces = [VariableFontFace(0, [Name("test", Language.get("en"))], [], [], 400, False, FontType.TRUETYPE, {})]
    is_collection_font = False

    time_before = time()
    font_file = FontFile(filename, font_faces, is_collection_font)
    time_after = time()

    assert font_file.filename == filename
    assert font_file.font_faces == font_faces
    assert font_file.is_collection_font == is_collection_font
    assert time_before <= font_file.last_loaded_time <= time_after
    assert font_faces[0].font_file == font_file

    last_loaded_time = 1000
    font_file = FontFile(filename, font_faces, is_collection_font, last_loaded_time)
    assert font_file.last_loaded_time == last_loaded_time

    with pytest.raises(FileNotFoundError) as exc_info:
        font_file = FontFile(Path("anything"), font_faces, is_collection_font)
    assert str(exc_info.value) == 'The file "anything" doesn\'t exist.'

    with pytest.raises(ValueError) as exc_info:
        font_file = FontFile(filename, [], is_collection_font)
    assert str(exc_info.value) == 'A FontFile need to contain at least 1 ABCFontFace.'


def test_filename_property():
    font_faces = [VariableFontFace(0, [Name("test", Language.get("en"))], [], [], 400, False, FontType.TRUETYPE, {})]
    font_file = FontFile(filename, font_faces, False)
    with pytest.raises(AttributeError) as exc_info:
        font_file.filename = filename


def test_font_faces_property():
    font_faces = [VariableFontFace(0, [Name("test", Language.get("en"))], [], [], 400, False, FontType.TRUETYPE, {})]
    font_file = FontFile(filename, font_faces, False)
    with pytest.raises(AttributeError) as exc_info:
        font_file.font_faces = font_faces


def test_is_collection_font_property():
    font_faces = [VariableFontFace(0, [Name("test", Language.get("en"))], [], [], 400, False, FontType.TRUETYPE, {})]
    font_file = FontFile(filename, font_faces, False)
    with pytest.raises(AttributeError) as exc_info:
        font_file.is_collection_font = True


def test_last_loaded_time_property():
    font_faces = [VariableFontFace(0, [Name("test", Language.get("en"))], [], [], 400, False, FontType.TRUETYPE, {})]
    font_file = FontFile(filename, font_faces, False)
    with pytest.raises(AttributeError) as exc_info:
        font_file.last_loaded_time = 1000


def test_from_font_path():
    font_mac_platform = Path(os.path.join(os.path.dirname(dir_path), "file", "fonts", "font_mac.TTF"))
    time_before = time()
    font_file = FontFile.from_font_path(font_mac_platform)
    time_after = time()

    expected_fonts = [
        NormalFontFace(
            0,
            [Name("Brushstroke Plain", Language.get("en"))],
            [Name("Brushstroke Plain", Language.get("en"))],
            400,
            False,
            False,
            FontType.TRUETYPE
        )
    ]

    assert font_file.filename == font_mac_platform
    assert font_file.font_faces == expected_fonts
    assert all(font_face.font_file == font_file for font_face in font_file.font_faces)
    assert time_before <= font_file.last_loaded_time <= time_after


def test_reload_font_file():
    font_mac_platform = Path(os.path.join(os.path.dirname(dir_path), "file", "fonts", "font_mac.TTF"))
    temp_font_path = Path(os.path.join(os.path.dirname(dir_path), "file", "fonts", "temp_font.TTF"))
    shutil.copy(font_mac_platform, temp_font_path)

    # Test before reloading the font file
    time_before = time()
    font_file = FontFile.from_font_path(temp_font_path)
    time_after = time()

    expected_fonts = [
        NormalFontFace(
            0,
            [Name("Brushstroke Plain", Language.get("en"))],
            [Name("Brushstroke Plain", Language.get("en"))],
            400,
            False,
            False,
            FontType.TRUETYPE
        )
    ]

    assert font_file.filename == temp_font_path
    assert font_file.font_faces == expected_fonts
    assert all(font_face.font_file == font_file for font_face in font_file.font_faces)
    assert time_before <= font_file.last_loaded_time <= time_after

    # Test after reloading the font file
    font_without_stat_table = Path(os.path.join(os.path.dirname(dir_path), "file", "fonts", "Cabin VF Beta Regular.ttf"))
    shutil.copy(font_without_stat_table, temp_font_path)

    time_before = time()
    font_file.reload_font_file()
    time_after = time()

    expected_fonts = [
        NormalFontFace(
            0,
            [Name("Cabin VF Beta", Language.get("en-US"))],
            [Name("Cabin VF Beta Regular", Language.get("en-US"))],
            400,
            False,
            False,
            FontType.TRUETYPE
        )
    ]

    assert font_file.filename == temp_font_path
    assert font_file.font_faces == expected_fonts
    assert all(font_face.font_file == font_file for font_face in font_file.font_faces)
    assert time_before <= font_file.last_loaded_time <= time_after

    os.remove(temp_font_path)

def test__eq__():
    font_mac_platform = Path(os.path.join(os.path.dirname(dir_path), "file", "fonts", "font_mac.TTF"))
    font_faces_1 = [
        VariableFontFace(0, [Name("test", Language.get("en"))], [], [], 400, False, FontType.TRUETYPE, {}),
        VariableFontFace(1, [Name("test", Language.get("en"))], [], [], 400, False, FontType.TRUETYPE, {}),
    ]
    font_faces_2 = [
        VariableFontFace(1, [Name("test", Language.get("en"))], [], [], 400, False, FontType.TRUETYPE, {}),
        VariableFontFace(0, [Name("test", Language.get("en"))], [], [], 400, False, FontType.TRUETYPE, {}),
    ]

    font_file_1 = FontFile(font_mac_platform, font_faces_1, False)
    font_file_2 = FontFile(font_mac_platform, font_faces_1, False)
    assert font_file_1 == font_file_2

    font_file_3 = FontFile(font_mac_platform, font_faces_2, False)
    assert font_file_1 == font_file_3

    font_collection_path = Path(os.path.join(os.path.dirname(dir_path), "file", "fonts", "truetype_font_collection.ttc"))
    font_file_4 = FontFile(font_collection_path, font_faces_1, True)
    assert font_file_1 != font_file_4

    font_file_5 = FontFile(font_mac_platform, font_faces_1, True)
    assert font_file_1 != font_file_5

    assert font_file_1 != "test"


def test__hash__():
    font_mac_platform = Path(os.path.join(os.path.dirname(dir_path), "file", "fonts", "font_mac.TTF"))
    font_faces_1 = [
        VariableFontFace(0, [Name("test", Language.get("en"))], [], [], 400, False, FontType.TRUETYPE, {}),
        VariableFontFace(1, [Name("test", Language.get("en"))], [], [], 400, False, FontType.TRUETYPE, {}),
    ]
    font_faces_2 = [
        VariableFontFace(1, [Name("test", Language.get("en"))], [], [], 400, False, FontType.TRUETYPE, {}),
        VariableFontFace(0, [Name("test", Language.get("en"))], [], [], 400, False, FontType.TRUETYPE, {}),
    ]

    font_file_1 = FontFile(font_mac_platform, font_faces_1, False)
    font_file_2 = FontFile(font_mac_platform, font_faces_1, False)
    assert isinstance(font_file_1, Hashable)
    assert {font_file_1} == {font_file_2}

    font_file_3 = FontFile(font_mac_platform, font_faces_2, False)
    assert {font_file_1} == {font_file_3}

    font_collection_path = Path(os.path.join(os.path.dirname(dir_path), "file", "fonts", "truetype_font_collection.ttc"))
    font_file_4 = FontFile(font_collection_path, font_faces_1, False)
    assert {font_file_1} != {font_file_4}

    font_file_5 = FontFile(font_mac_platform, font_faces_1, True)
    assert {font_file_1} != {font_file_5}

    assert {font_file_1} != {"test"}


def test__repr__():
    font_mac_platform = Path(os.path.join(os.path.dirname(dir_path), "file", "fonts", "font_mac.TTF"))
    font_faces = [
        VariableFontFace(0, [Name("test", Language.get("en"))], [], [], 400, False, FontType.TRUETYPE, {}),
    ]
    last_loaded_time = 1000

    font_file = FontFile(font_mac_platform, font_faces, False, last_loaded_time)
    assert repr(font_file) == f'FontFile(Filename="{font_mac_platform}", Font faces="[VariableFontFace(Font index="0", Family names="[Name(value="test", lang_code="en")]", Exact names="[]", Weight="400", Italic="False", Glyph emboldened="False", Font type="TRUETYPE", Named instance coordinates="{{}}")]", Is collection Font="False", Last loaded time="1000")'
