import collections
import os

import pytest
from langcodes import Language

from font_collector import (
    FontType,
    InvalidVariableFontFaceException,
    Name,
    NormalFontFace,
    VariableFontFace
)
from font_collector.font.factory_abc_font_face import FactoryABCFontFace

dir_path = os.path.dirname(os.path.realpath(__file__))


def test_font_without_os2_table():
    font_mac_platform = os.path.join(os.path.dirname(dir_path), "file", "fonts", "font_mac.TTF")
    fonts, is_collection_font = FactoryABCFontFace.from_font_path(font_mac_platform)
    expected_is_collection_font = False
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

    assert is_collection_font == expected_is_collection_font
    assert fonts == expected_fonts


def test_font_collection():
    font_collection_path = os.path.join(os.path.dirname(dir_path), "file", "fonts", "truetype_font_collection.ttc")
    fonts, is_collection_font = FactoryABCFontFace.from_font_path(font_collection_path)
    expected_is_collection_font = True
    expected_fonts = [
        NormalFontFace(
            0,
            [Name("Gulim", Language.get("en-US")), Name("굴림", Language.get("ko-KR"))],
            [Name("Gulim", Language.get("en-US")), Name("굴림", Language.get("ko-KR"))],
            400,
            False,
            False,
            FontType.TRUETYPE
        ),
        NormalFontFace(
            1,
            [Name("GulimChe", Language.get("en-US")), Name("굴림체", Language.get("ko-KR"))],
            [Name("GulimChe", Language.get("en-US")), Name("굴림체", Language.get("ko-KR"))],
            400,
            False,
            False,
            FontType.TRUETYPE
        ),
        NormalFontFace(
            2,
            [Name("Dotum", Language.get("en-US")), Name("돋움", Language.get("ko-KR"))],
            [Name("Dotum", Language.get("en-US")), Name("돋움", Language.get("ko-KR"))],
            400,
            False,
            False,
            FontType.TRUETYPE
        ),
        NormalFontFace(
            3,
            [Name("DotumChe", Language.get("en-US")), Name("돋움체", Language.get("ko-KR"))],
            [Name("DotumChe", Language.get("en-US")), Name("돋움체", Language.get("ko-KR"))],
            400,
            False,
            False,
            FontType.TRUETYPE
        )
    ]

    assert is_collection_font == expected_is_collection_font
    assert collections.Counter(fonts) == collections.Counter(expected_fonts)


def test_font_with_fvar_table_but_without_stat_table():
    font_without_stat_table = os.path.join(os.path.dirname(dir_path), "file", "fonts", "Cabin VF Beta Regular.ttf")
    fonts, is_collection_font = FactoryABCFontFace.from_font_path(font_without_stat_table)
    expected_is_collection_font = False
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

    assert is_collection_font == expected_is_collection_font
    assert fonts == expected_fonts


def test_font_without_axis_value():
    font_without_axis_value = os.path.join(os.path.dirname(dir_path), "file", "fonts", "font_without axis_value.ttf")
    fonts, is_collection_font = FactoryABCFontFace.from_font_path(font_without_axis_value)
    expected_is_collection_font = False
    expected_fonts = [
        VariableFontFace(
            0,
            [Name("Inter", Language.get("en-US"))],
            [],
            [Name("Regular", Language.get("en-US"))],
            400,
            False,
            FontType.TRUETYPE,
            {"wght": 100.0, "slnt": 0.0},
        )
    ]

    assert is_collection_font == expected_is_collection_font
    assert fonts == expected_fonts


def test_variable_font_with_invalid_fvar_defaultValue():
    font_path = os.path.join(os.path.dirname(dir_path), "file", "variable font tests", "Test #1", "Test #1.ttf")
    fonts, is_collection_font = FactoryABCFontFace.from_font_path(font_path)
    expected_is_collection_font = False
    expected_font = [NormalFontFace(
        0,
        [Name("Advent Pro", Language.get("en-US"))],
        [Name("Advent Pro Italic", Language.get("en-US"))],
        400,
        True,
        False,
        FontType.TRUETYPE,
    )]

    assert is_collection_font == expected_is_collection_font
    assert fonts == expected_font

def test_variable_font_with_0_instance_fvar():
    font_path = os.path.join(os.path.dirname(dir_path), "file", "fonts", "fvar_with_0_instance.ttf")
    fonts, is_collection_font = FactoryABCFontFace.from_font_path(font_path)
    expected_is_collection_font = False
    expected_font = [NormalFontFace(
        0,
        [Name("Signika Medium", Language.get("en-US"))],
        [Name("Signika Medium", Language.get("en-US"))],
        500,
        False,
        False,
        FontType.TRUETYPE,
    )]

    assert is_collection_font == expected_is_collection_font
    assert fonts == expected_font

def test_variable_font_with_empty_axis_value_array():
    font_path = os.path.join(os.path.dirname(dir_path), "file", "variable font tests", "Test #2", "Test #2.ttf")
    fonts, is_collection_font = FactoryABCFontFace.from_font_path(font_path)
    expected_is_collection_font = False
    expected_font = [
        VariableFontFace(
            0,
            [Name("Alegreya", Language.get("en-US"))],
            [],
            [Name("Italic", Language.get("en-US"))],
            400,
            False,
            FontType.TRUETYPE,
            {'wght': 400.0}
        )
    ]

    assert is_collection_font == expected_is_collection_font
    assert fonts == expected_font

def test_variable_font_without_fvar_table():
    font_path = os.path.join(os.path.dirname(dir_path), "file", "variable font tests", "Test #3", "Test #3.ttf")
    fonts, is_collection_font = FactoryABCFontFace.from_font_path(font_path)
    expected_is_collection_font = False
    expected_font = [NormalFontFace(
        0,
        [Name("Advent Pro", Language.get("en-US"))],
        [Name("Advent Pro Italic", Language.get("en-US"))],
        300,
        True,
        False,
        FontType.TRUETYPE,
    )]

    assert is_collection_font == expected_is_collection_font
    assert fonts == expected_font


def test_variable_font_with_axis_value_format_4_one_axis_value_record():
    # The AxisValue Format 4 contain only 1 AxisValue in the AxisValueRecord

    font_path = os.path.join(os.path.dirname(dir_path), "file", "variable font tests", "Test #4", "Test #4.ttf")
    fonts, is_collection_font = FactoryABCFontFace.from_font_path(font_path)
    expected_is_collection_font = False
    expected_fonts = [
        VariableFontFace(
            0,
            [Name("Alegreya", Language.get("en-US"))],
            [Name("", Language.get("en-US"))],
            [Name("Italic", Language.get("en-US"))],
            400,
            True,
            FontType.TRUETYPE,
            {"wght": 400.0},
        ),
        VariableFontFace(
            0,
            [Name("Alegreya", Language.get("en-US"))],
            [Name("Medium", Language.get("en-US"))],
            [Name("Medium Italic", Language.get("en-US"))],
            500,
            True,
            FontType.TRUETYPE,
            {"wght": 500.0},
        ),
        VariableFontFace(
            0,
            [Name("Alegreya", Language.get("en-US"))],
            [Name("", Language.get("en-US"))],
            [Name("Bold Italic", Language.get("en-US"))],
            700,
            True,
            FontType.TRUETYPE,
            {"wght": 700.0},
        ),
        VariableFontFace(
            0,
            [Name("Alegreya", Language.get("en-US"))],
            [Name("Roman numerals", Language.get("en-US"))],
            [Name("Roman numerals Italic", Language.get("en-US"))],
            800,
            True,
            FontType.TRUETYPE,
            {"wght": 800.0},
        ),
        VariableFontFace(
            0,
            [Name("Alegreya", Language.get("en-US"))],
            [Name("Black", Language.get("en-US"))],
            [Name("Black Italic", Language.get("en-US"))],
            900,
            True,
            FontType.TRUETYPE,
            {"wght": 900.0},
        ),
    ]

    assert is_collection_font == expected_is_collection_font
    assert collections.Counter(fonts) == collections.Counter(expected_fonts)


def test_variable_font_with_axis_value_format_4_multiple_axis_value_record():
    # The AxisValue Format 4 contain multiple AxisValue in the AxisValueRecord

    font_path = os.path.join(os.path.dirname(dir_path), "file", "variable font tests", "Test #5", "Test #5.ttf")
    fonts, is_collection_font = FactoryABCFontFace.from_font_path(font_path)
    expected_is_collection_font = False
    expected_fonts = [
        VariableFontFace(
            0,
            [Name("Alegreya", Language.get("en-US"))],
            [Name("", Language.get("en-US"))],
            [Name("Italic", Language.get("en-US"))],
            400,
            True,
            FontType.TRUETYPE,
            {"wght": 400.0},
        ),
        VariableFontFace(
            0,
            [Name("Alegreya", Language.get("en-US"))],
            [Name("Medium", Language.get("en-US"))],
            [Name("Medium Italic", Language.get("en-US"))],
            500,
            True,
            FontType.TRUETYPE,
            {"wght": 500.0},
        ),
        VariableFontFace(
            0,
            [Name("Alegreya", Language.get("en-US"))],
            [Name("", Language.get("en-US"))],
            [Name("Bold Italic", Language.get("en-US"))],
            700,
            True,
            FontType.TRUETYPE,
            {"wght": 700.0},
        ),
        VariableFontFace(
            0,
            [Name("Alegreya", Language.get("en-US"))],
            [Name("Roman numerals", Language.get("en-US"))],
            [Name("Roman numerals", Language.get("en-US"))],
            400,
            False,
            FontType.TRUETYPE,
            {"wght": 800.0},
        ),
        VariableFontFace(
            0,
            [Name("Alegreya", Language.get("en-US"))],
            [Name("Black", Language.get("en-US"))],
            [Name("Black Italic", Language.get("en-US"))],
            900,
            True,
            FontType.TRUETYPE,
            {"wght": 900.0},
        ),
    ]

    assert is_collection_font == expected_is_collection_font
    assert collections.Counter(fonts) == collections.Counter(expected_fonts)


def test_variable_font_with_invalid_elided_fallback_nameid():

    font_path = os.path.join(os.path.dirname(dir_path), "file", "variable font tests", "Test #6", "Test #6.ttf")
    fonts, is_collection_font = FactoryABCFontFace.from_font_path(font_path)
    expected_is_collection_font = False
    expected_fonts = [
        VariableFontFace(
            0,
            [Name("Advent Pro", Language.get("en-US"))],
            [],
            [Name("Regular", Language.get("en-US"))],
            400,
            False,
            FontType.TRUETYPE,
            {'wdth': 100.0, 'wght': 100.0},
        )
    ]

    assert is_collection_font == expected_is_collection_font
    assert fonts == expected_fonts


def test_variable_font_match_with_axis_value_format_4_and_axis_format_1():
    # The NamedInstance "wght" == 800 will take the AxisValue Format 4 weight and the AxisValue Format 1 "ital".

    font_path = os.path.join(os.path.dirname(dir_path), "file", "variable font tests", "Test #7", "Test #7.ttf")
    fonts, is_collection_font = FactoryABCFontFace.from_font_path(font_path)
    expected_is_collection_font = False
    expected_fonts = [
        VariableFontFace(
            0,
            [Name("Alegreya", Language.get("en-US"))],
            [Name("", Language.get("en-US"))],
            [Name("Italic", Language.get("en-US"))],
            400,
            True,
            FontType.TRUETYPE,
            {"wght": 400.0},
        ),
        VariableFontFace(
            0,
            [Name("Alegreya", Language.get("en-US"))],
            [Name("Medium", Language.get("en-US"))],
            [Name("Medium Italic", Language.get("en-US"))],
            500,
            True,
            FontType.TRUETYPE,
            {"wght": 500.0},
        ),
        VariableFontFace(
            0,
            [Name("Alegreya", Language.get("en-US"))],
            [Name("", Language.get("en-US"))],
            [Name("Bold Italic", Language.get("en-US"))],
            700,
            True,
            FontType.TRUETYPE,
            {"wght": 700.0},
        ),
        VariableFontFace(
            0,
            [Name("Alegreya", Language.get("en-US"))],
            [Name("ExtraBold", Language.get("en-US"))],
            [Name("ExtraBold Italic", Language.get("en-US"))],
            755,
            True,
            FontType.TRUETYPE,
            {"wght": 800.0},
        ),
        VariableFontFace(
            0,
            [Name("Alegreya", Language.get("en-US"))],
            [Name("Black", Language.get("en-US"))],
            [Name("Black Italic", Language.get("en-US"))],
            900,
            True,
            FontType.TRUETYPE,
            {"wght": 900.0},
        ),
    ]

    assert is_collection_font == expected_is_collection_font
    assert collections.Counter(fonts) == collections.Counter(expected_fonts)


def test_variable_font_duplicate_font_face():
    font_path = os.path.join(os.path.dirname(dir_path), "file", "variable font tests", "Test #8", "Test #8.ttf")
    fonts, is_collection_font = FactoryABCFontFace.from_font_path(font_path)
    expected_is_collection_font = False
    expected_fonts = [
        VariableFontFace(
            0,
            [Name("Alegreya", Language.get("en-US"))],
            [Name("", Language.get("en-US"))],
            [Name("Italic", Language.get("en-US"))],
            400,
            True,
            FontType.TRUETYPE,
            {"wght": 400.0},
        ),
        VariableFontFace(
            0,
            [Name("Alegreya", Language.get("en-US"))],
            [Name("Medium", Language.get("en-US"))],
            [Name("Medium Italic", Language.get("en-US"))],
            500,
            True,
            FontType.TRUETYPE,
            {"wght": 500.0},
        ),
        VariableFontFace(
            0,
            [Name("Alegreya", Language.get("en-US"))],
            [Name("", Language.get("en-US"))],
            [Name("Bold Italic", Language.get("en-US"))],
            700,
            True,
            FontType.TRUETYPE,
            {"wght": 700.0},
        ),
        VariableFontFace(
            0,
            [Name("Alegreya", Language.get("en-US"))],
            [Name("Black", Language.get("en-US"))],
            [Name("Black Italic", Language.get("en-US"))],
            900,
            True,
            FontType.TRUETYPE,
            {"wght": 800.0},
        ),
    ]

    assert is_collection_font == expected_is_collection_font
    assert collections.Counter(fonts) == collections.Counter(expected_fonts)


def test_variable_font_with_multiple_lang_name_id():
    font_path = os.path.join(os.path.dirname(dir_path), "file", "variable font tests", "Test #9", "Test #9.ttf")
    fonts, is_collection_font = FactoryABCFontFace.from_font_path(font_path)
    expected_is_collection_font = False
    expected_fonts = [
        VariableFontFace(
            0,
            [Name("family text", Language.get("fr-CA"))],
            [Name("", Language.get("en-US")), Name("", Language.get("fr-CA"))],
            [Name("Italic", Language.get("en-US")), Name("Italic", Language.get("fr-CA"))],
            400,
            True,
            FontType.TRUETYPE,
            {"wght": 400.0},
        ),
        VariableFontFace(
            0,
            [Name("family text", Language.get("fr-CA"))],
            [Name("Medium", Language.get("en-US")), Name("Medium", Language.get("fr-CA")), Name("Medium French Canada", Language.get("fr-CA"))],
            [Name("Medium Italic", Language.get("en-US")), Name("Medium Italic", Language.get("fr-CA")), Name("Medium French Canada Italic", Language.get("fr-CA"))],
            500,
            True,
            FontType.TRUETYPE,
            {"wght": 500.0},
        ),
        VariableFontFace(
            0,
            [Name("family text", Language.get("fr-CA"))],
            [Name("", Language.get("en-US")), Name("", Language.get("fr-CA"))],
            [Name("Bold Italic", Language.get("en-US")), Name("Bold Italic", Language.get("fr-CA")), Name("Bold French Canada Italic", Language.get("fr-CA"))],
            700,
            True,
            FontType.TRUETYPE,
            {"wght": 700.0},
        ),
        VariableFontFace(
            0,
            [Name("family text", Language.get("fr-CA"))],
            [Name("ExtraBold", Language.get("fr-CA"))],
            [Name("ExtraBold Italic", Language.get("fr-CA"))],
            800,
            True,
            FontType.TRUETYPE,
            {"wght": 800.0},
        ),
        VariableFontFace(
            0,
            [Name("family text", Language.get("fr-CA"))],
            [Name("Black", Language.get("en-US")), Name("Black", Language.get("fr-CA")), Name("Black French Canada", Language.get("fr-CA"))],
            [Name("Black Italic", Language.get("en-US")), Name("Black Italic", Language.get("fr-CA")), Name("Black French Canada Italic", Language.get("fr-CA"))],
            900,
            True,
            FontType.TRUETYPE,
            {"wght": 900.0},
        ),
    ]

    assert is_collection_font == expected_is_collection_font
    assert collections.Counter(fonts) == collections.Counter(expected_fonts)


def test_stat_invalid_axis_value_id():
    font_path = os.path.join(os.path.dirname(dir_path), "file", "variable font tests", "Test #10", "Test #10.ttf")
    fonts, is_collection_font = FactoryABCFontFace.from_font_path(font_path)
    expected_is_collection_font = False
    expected_font = [NormalFontFace(
        0,
        [Name("Alegreya", Language.get("en-US"))],
        [Name("Alegreya Italic", Language.get("en-US"))],
        400,
        True,
        False,
        FontType.TRUETYPE,
    )]

    assert is_collection_font == expected_is_collection_font
    assert fonts == expected_font


def test_without_ElidedFallbackNameID():
    font_path = os.path.join(os.path.dirname(dir_path), "file", "variable font tests", "Test #11", "Test #11.ttf")
    fonts, is_collection_font = FactoryABCFontFace.from_font_path(font_path)
    expected_is_collection_font = False
    expected_fonts = [
        VariableFontFace(
            0,
            [Name("Advent Pro", Language.get("en-US"))],
            [Name("", Language.get("en-US"))],
            [Name("Normal", Language.get("en-US"))],
            100,
            True,
            FontType.TRUETYPE,
            {'wdth': 100.0, 'wght': 100.0},
        ),
        VariableFontFace(
            0,
            [Name("Advent Pro", Language.get("en-US"))],
            [Name("", Language.get("en-US"))],
            [Name("Normal", Language.get("en-US"))],
            200,
            True,
            FontType.TRUETYPE,
            {'wdth': 100.0, 'wght': 200.0},
        ),
        VariableFontFace(
            0,
            [Name("Advent Pro", Language.get("en-US"))],
            [Name("", Language.get("en-US"))],
            [Name("Normal", Language.get("en-US"))],
            300,
            True,
            FontType.TRUETYPE,
            {'wdth': 100.0, 'wght': 300.0},
        ),
        VariableFontFace(
            0,
            [Name("Advent Pro", Language.get("en-US"))],
            [Name("", Language.get("en-US"))],
            [Name("Normal", Language.get("en-US"))],
            400,
            True,
            FontType.TRUETYPE,
            {'wdth': 100.0, 'wght': 400.0},
        ),
        VariableFontFace(
            0,
            [Name("Advent Pro", Language.get("en-US"))],
            [Name("", Language.get("en-US"))],
            [Name("Normal", Language.get("en-US"))],
            500,
            True,
            FontType.TRUETYPE,
            {'wdth': 100.0, 'wght': 500.0},
        ),
        VariableFontFace(
            0,
            [Name("Advent Pro", Language.get("en-US"))],
            [Name("", Language.get("en-US"))],
            [Name("Normal", Language.get("en-US"))],
            600,
            True,
            FontType.TRUETYPE,
            {'wdth': 100.0, 'wght': 600.0},
        ),
        VariableFontFace(
            0,
            [Name("Advent Pro", Language.get("en-US"))],
            [Name("", Language.get("en-US"))],
            [Name("Normal", Language.get("en-US"))],
            700,
            True,
            FontType.TRUETYPE,
            {'wdth': 100.0, 'wght': 700.0},
        ),
        VariableFontFace(
            0,
            [Name("Advent Pro", Language.get("en-US"))],
            [Name("", Language.get("en-US"))],
            [Name("Normal", Language.get("en-US"))],
            800,
            True,
            FontType.TRUETYPE,
            {'wdth': 100.0, 'wght': 800.0},
        ),
        VariableFontFace(
            0,
            [Name("Advent Pro", Language.get("en-US"))],
            [Name("", Language.get("en-US"))],
            [Name("Normal", Language.get("en-US"))],
            900,
            True,
            FontType.TRUETYPE,
            {'wdth': 100.0, 'wght': 900.0},
        )
    ]

    assert is_collection_font == expected_is_collection_font
    assert collections.Counter(fonts) == collections.Counter(expected_fonts)


def test_variable_font_without_DesignAxisRecord():

    font_path = os.path.join(os.path.dirname(dir_path), "file", "variable font tests", "Test #12", "Test #12.ttf")

    with pytest.raises(InvalidVariableFontFaceException) as exc_info:
        FactoryABCFontFace.from_font_path(font_path)
    assert str(exc_info.value) == "The font has a stat table, but it doesn't have any DesignAxisRecord"


def test_variable_font_without_invalid_name_id():
    font_path = os.path.join(os.path.dirname(dir_path), "file", "variable font tests", "Test #13", "Test #13.ttf")
    fonts, is_collection_font = FactoryABCFontFace.from_font_path(font_path)
    expected_is_collection_font = False
    expected_fonts = [
        NormalFontFace(
            0,
            [Name("Alegreya", Language.get("en-US"))],
            [Name("Alegreya Italic", Language.get("en-US"))],
            400,
            True,
            False,
            FontType.TRUETYPE,
        ),
    ]

    assert is_collection_font == expected_is_collection_font
    assert collections.Counter(fonts) == collections.Counter(expected_fonts)


def test_opentype_font():
    font_path = os.path.join(os.path.dirname(dir_path), "file", "fonts", "PENBOX.otf")
    fonts, is_collection_font = FactoryABCFontFace.from_font_path(font_path)
    expected_is_collection_font = False
    expected_fonts = [
        NormalFontFace(
            0,
            [Name("PENBOX", Language.get("en-US"))],
            [Name("PENBOXRegular", Language.get("en-US"))],
            400,
            False,
            False,
            FontType.OPENTYPE,
        ),
    ]

    assert is_collection_font == expected_is_collection_font
    assert collections.Counter(fonts) == collections.Counter(expected_fonts)
