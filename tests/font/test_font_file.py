import collections
import os
from time import time
import pytest
import string
from font_collector import FontFile, FontType, Name, NormalFontFace, VariableFontFace
from langcodes import Language
from typing import Hashable

dir_path = os.path.dirname(os.path.realpath(__file__))

filename = os.path.join(os.path.dirname(dir_path), "file", "fonts", "Asap-VariableFont_wdth,wght.ttf")

def test__init__():
    filename_upper = filename.upper()
    font_faces = [VariableFontFace(0, [Name("test", Language.get("en"))], [], [], 400, False, FontType.TRUETYPE, {})]

    time_before = time()
    font_file = FontFile(filename_upper, font_faces)
    time_after = time()

    assert font_file.filename == filename
    assert font_file.font_faces == font_faces
    assert time_before <= font_file.last_loaded_time <= time_after
    assert font_faces[0].font_file == font_file

    last_loaded_time = 1000
    font_file = FontFile(filename_upper, font_faces, last_loaded_time)
    assert font_file.last_loaded_time == last_loaded_time

    with pytest.raises(FileNotFoundError) as exc_info:
        font_file = FontFile("anything", font_faces)
    assert str(exc_info.value) == 'The file "anything" doesn\'t exist.'

    with pytest.raises(ValueError) as exc_info:
        font_file = FontFile(filename, [])
    assert str(exc_info.value) == 'A FontFile need to contain at least 1 ABCFontFace.'


def test_filename_property():
    font_faces = [VariableFontFace(0, [Name("test", Language.get("en"))], [], [], 400, False, FontType.TRUETYPE, {})]
    font_file = FontFile(filename, font_faces)
    with pytest.raises(AttributeError) as exc_info:
        font_file.filename = filename
    assert str(exc_info.value) == "property 'filename' of 'FontFile' object has no setter"

def test_font_faces_property():
    font_faces = [VariableFontFace(0, [Name("test", Language.get("en"))], [], [], 400, False, FontType.TRUETYPE, {})]
    font_file = FontFile(filename, font_faces)
    with pytest.raises(AttributeError) as exc_info:
        font_file.font_faces = font_faces
    assert str(exc_info.value) == "property 'font_faces' of 'FontFile' object has no setter"

def test_last_loaded_time_property():
    font_faces = [VariableFontFace(0, [Name("test", Language.get("en"))], [], [], 400, False, FontType.TRUETYPE, {})]
    font_file = FontFile(filename, font_faces)
    with pytest.raises(AttributeError) as exc_info:
        font_file.last_loaded_time = 1000
    assert str(exc_info.value) == "property 'last_loaded_time' of 'FontFile' object has no setter"

def test_from_font_path():
    font_mac_platform = os.path.join(os.path.dirname(dir_path), "file", "fonts", "font_mac.TTF")
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
    assert time_before <= font_file.last_loaded_time <= time_after

def test__eq__():
    font_mac_platform = os.path.join(os.path.dirname(dir_path), "file", "fonts", "font_mac.TTF")
    font_faces_1 = [
        VariableFontFace(0, [Name("test", Language.get("en"))], [], [], 400, False, FontType.TRUETYPE, {}),
        VariableFontFace(1, [Name("test", Language.get("en"))], [], [], 400, False, FontType.TRUETYPE, {}),
    ]
    font_faces_2 = [
        VariableFontFace(1, [Name("test", Language.get("en"))], [], [], 400, False, FontType.TRUETYPE, {}),
        VariableFontFace(0, [Name("test", Language.get("en"))], [], [], 400, False, FontType.TRUETYPE, {}),
    ]

    font_file_1 = FontFile(font_mac_platform, font_faces_1)
    font_file_2 = FontFile(font_mac_platform, font_faces_1)
    font_file_1 == font_file_2

    font_file_3 = FontFile(font_mac_platform, font_faces_2)
    font_file_1 == font_file_3

    font_collection_path = os.path.join(os.path.dirname(dir_path), "file", "fonts", "truetype_font_collection.ttc")
    font_file_4 = FontFile(font_collection_path, font_faces_1)
    font_file_1 != font_file_4

def test__hash__():
    font_mac_platform = os.path.join(os.path.dirname(dir_path), "file", "fonts", "font_mac.TTF")
    font_faces_1 = [
        VariableFontFace(0, [Name("test", Language.get("en"))], [], [], 400, False, FontType.TRUETYPE, {}),
        VariableFontFace(1, [Name("test", Language.get("en"))], [], [], 400, False, FontType.TRUETYPE, {}),
    ]
    font_faces_2 = [
        VariableFontFace(1, [Name("test", Language.get("en"))], [], [], 400, False, FontType.TRUETYPE, {}),
        VariableFontFace(0, [Name("test", Language.get("en"))], [], [], 400, False, FontType.TRUETYPE, {}),
    ]

    font_file_1 = FontFile(font_mac_platform, font_faces_1)
    font_file_2 = FontFile(font_mac_platform, font_faces_1)
    assert isinstance(font_file_1, Hashable)
    {font_file_1} == {font_file_2}

    font_file_3 = FontFile(font_mac_platform, font_faces_2)
    {font_file_1} == {font_file_3}

    font_collection_path = os.path.join(os.path.dirname(dir_path), "file", "fonts", "truetype_font_collection.ttc")
    font_file_4 = FontFile(font_collection_path, font_faces_1)
    {font_file_1} != {font_file_4}

def test__repr__():
    font_mac_platform = os.path.join(os.path.dirname(dir_path), "file", "fonts", "font_mac.TTF")
    font_faces = [
        VariableFontFace(0, [Name("test", Language.get("en"))], [], [], 400, False, FontType.TRUETYPE, {}),
    ]
    last_loaded_time = 1000

    font_file = FontFile(font_mac_platform, font_faces, last_loaded_time)
    assert repr(font_file) == f'FontFile(Filename="{font_mac_platform}", Font faces="[VariableFontFace(Font index="0", Family names="[Name(value="test", lang_code="en")]", Exact names="[]", Weight="400", Italic="False", Glyph emboldened="False", Font type="TRUETYPE", Named instance coordinates="{{}}")]", Last loaded time="1000")'