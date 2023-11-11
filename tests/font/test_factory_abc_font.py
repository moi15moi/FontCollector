import collections
import os

import pytest
from font_collector import FactoryABCFont, Font, FontType, Name, VariableFont, InvalidVariableFontException
from langcodes import Language


dir_path = os.path.dirname(os.path.realpath(__file__))


def test_font_without_os2_table():
    font_mac_platform = os.path.join(os.path.dirname(dir_path), "fonts", "font_mac.TTF")
    fonts = FactoryABCFont.from_font_path(font_mac_platform)
    expected_fonts = [
        Font(
            font_mac_platform,
            0,
            set([Name("Brushstroke Plain", Language.get("en"))]),
            set([Name("Brushstroke Plain", Language.get("en"))]),
            400,
            False,
            False,
            FontType.TRUETYPE
        )
    ]

    assert fonts == expected_fonts


def test_font_collection():
    font_collection_path = os.path.join(os.path.dirname(dir_path), "fonts", "font_collection.ttc")
    fonts = FactoryABCFont.from_font_path(font_collection_path)
    expected_fonts = [
        Font(
            font_collection_path,
            0,
            set([Name("Gulim", Language.get("en")), Name("굴림", Language.get("ko"))]),
            set([Name("Gulim", Language.get("en")), Name("굴림", Language.get("ko"))]),
            400,
            False,
            False,
            FontType.TRUETYPE
        ),
        Font(
            font_collection_path,
            1,
            set([Name("GulimChe", Language.get("en")), Name("굴림체", Language.get("ko"))]),
            set([Name("GulimChe", Language.get("en")), Name("굴림체", Language.get("ko"))]),
            400,
            False,
            False,
            FontType.TRUETYPE
        ),
        Font(
            font_collection_path,
            2,
            set([Name("Dotum", Language.get("en")), Name("돋움", Language.get("ko"))]),
            set([Name("Dotum", Language.get("en")), Name("돋움", Language.get("ko"))]),
            400,
            False,
            False,
            FontType.TRUETYPE
        ),
        Font(
            font_collection_path,
            3,
            set([Name("DotumChe", Language.get("en")), Name("돋움체", Language.get("ko"))]),
            set([Name("DotumChe", Language.get("en")), Name("돋움체", Language.get("ko"))]),
            400,
            False,
            False,
            FontType.TRUETYPE
        )
    ]

    assert collections.Counter(fonts) == collections.Counter(expected_fonts)


def test_font_with_fvar_table_but_without_stat_table():
    font_without_stat_table = os.path.join(os.path.dirname(dir_path), "fonts", "Cabin VF Beta Regular.ttf")
    fonts = FactoryABCFont.from_font_path(font_without_stat_table)
    expected_fonts = [
        Font(
            font_without_stat_table,
            0,
            set([Name("Cabin VF Beta", Language.get("en"))]),
            set([Name("Cabin VF Beta Regular", Language.get("en"))]),
            400,
            False,
            False,
            FontType.TRUETYPE
        )
    ]

    assert fonts == expected_fonts


def test_font_without_axis_value():
    font_without_axis_value = os.path.join(os.path.dirname(dir_path), "fonts", "font_without axis_value.ttf")
    fonts = FactoryABCFont.from_font_path(font_without_axis_value)
    expected_fonts = [
        VariableFont(
            font_without_axis_value,
            0,
            set([Name("Inter", Language.get("en"))]),
            set([Name("", Language.get("en"))]),
            set([Name("Regular", Language.get("en"))]),
            400,
            False,
            FontType.TRUETYPE,
            {"wght": 100.0, "slnt": 0.0},
        )
    ]

    assert fonts == expected_fonts


def test_variable_font_with_invalid_fvar_defaultValue():
    font_path = os.path.join(os.path.dirname(dir_path), "variable font tests", "Test #1", "Test #1.ttf")
    fonts = FactoryABCFont.from_font_path(font_path)
    expected_font = [Font(
        font_path, 
        0, 
        set([Name("Advent Pro", Language.get("en"))]),
        set([Name("Advent Pro Italic", Language.get("en"))]),
        400, 
        True, 
        False,
        FontType.TRUETYPE,
    )]
    
    assert fonts == expected_font


def test_variable_font_with_empty_axis_value_array():
    font_path = os.path.join(os.path.dirname(dir_path), "variable font tests", "Test #2", "Test #2.ttf")
    fonts = FactoryABCFont.from_font_path(font_path)
    expected_font = [
        VariableFont(
            font_path, 
            0, 
            set([Name("Alegreya", Language.get("en"))]), 
            set([Name("", Language.get("en"))]), 
            set([Name("Italic", Language.get("en"))]),
            400, 
            False, 
            FontType.TRUETYPE,
            {'wght': 400.0}
        )
    ]

    assert fonts == expected_font

def test_variable_font_without_fvar_table():
    font_path = os.path.join(os.path.dirname(dir_path), "variable font tests", "Test #3", "Test #3.ttf")
    fonts = FactoryABCFont.from_font_path(font_path)


    expected_font = [Font(
        font_path, 
        0, 
        set([Name("Advent Pro", Language.get("en"))]), 
        set([Name("Advent Pro Italic", Language.get("en"))]),
        300, 
        True, 
        False, 
        FontType.TRUETYPE,
    )]

    assert fonts == expected_font


def test_variable_font_with_axis_value_format_4_one_axis_value_record():
    # The AxisValue Format 4 contain only 1 AxisValue in the AxisValueRecord

    font_path = os.path.join(os.path.dirname(dir_path), "variable font tests", "Test #4", "Test #4.ttf")

    fonts = FactoryABCFont.from_font_path(font_path)
    expected_fonts = [
        VariableFont(
            font_path,
            0,
            set([Name("Alegreya", Language.get("en"))]),
            set([Name("", Language.get("en"))]),
            set([Name("Italic", Language.get("en"))]),
            400,
            True,
            FontType.TRUETYPE,
            {"wght": 400.0},
        ),
        VariableFont(
            font_path,
            0,
            set([Name("Alegreya", Language.get("en"))]),
            set([Name("Medium", Language.get("en"))]),
            set([Name("Medium Italic", Language.get("en"))]),
            500,
            True,
            FontType.TRUETYPE,
            {"wght": 500.0},
        ),
        VariableFont(
            font_path,
            0,
            set([Name("Alegreya", Language.get("en"))]),
            set([Name("", Language.get("en"))]),
            set([Name("Bold Italic", Language.get("en"))]),
            700,
            True,
            FontType.TRUETYPE,
            {"wght": 700.0},
        ),
        VariableFont(
            font_path,
            0,
            set([Name("Alegreya", Language.get("en"))]),
            set([Name("Roman numerals", Language.get("en"))]),
            set([Name("Roman numerals Italic", Language.get("en"))]),
            800,
            True,
            FontType.TRUETYPE,
            {"wght": 800.0},
        ),
        VariableFont(
            font_path,
            0,
            set([Name("Alegreya", Language.get("en"))]),
            set([Name("Black", Language.get("en"))]),
            set([Name("Black Italic", Language.get("en"))]),
            900,
            True,
            FontType.TRUETYPE,
            {"wght": 900.0},
        ),
    ]


    assert collections.Counter(fonts) == collections.Counter(expected_fonts)


def test_variable_font_with_axis_value_format_4_multiple_axis_value_record():
    # The AxisValue Format 4 contain multiple AxisValue in the AxisValueRecord

    font_path = os.path.join(os.path.dirname(dir_path), "variable font tests", "Test #5", "Test #5.ttf")

    fonts = FactoryABCFont.from_font_path(font_path)
    expected_fonts = [
        VariableFont(
            font_path,
            0,
            set([Name("Alegreya", Language.get("en"))]),
            set([Name("", Language.get("en"))]),
            set([Name("Italic", Language.get("en"))]),
            400,
            True,
            FontType.TRUETYPE,
            {"wght": 400.0},
        ),
        VariableFont(
            font_path,
            0,
            set([Name("Alegreya", Language.get("en"))]),
            set([Name("Medium", Language.get("en"))]),
            set([Name("Medium Italic", Language.get("en"))]),
            500,
            True,
            FontType.TRUETYPE,
            {"wght": 500.0},
        ),
        VariableFont(
            font_path,
            0,
            set([Name("Alegreya", Language.get("en"))]),
            set([Name("", Language.get("en"))]),
            set([Name("Bold Italic", Language.get("en"))]),
            700,
            True,
            FontType.TRUETYPE,
            {"wght": 700.0},
        ),
        VariableFont(
            font_path,
            0,
            set([Name("Alegreya", Language.get("en"))]),
            set([Name("Roman numerals", Language.get("en"))]),
            set([Name("Roman numerals", Language.get("en"))]),
            400,
            False,
            FontType.TRUETYPE,
            {"wght": 800.0},
        ),
        VariableFont(
            font_path,
            0,
            set([Name("Alegreya", Language.get("en"))]),
            set([Name("Black", Language.get("en"))]),
            set([Name("Black Italic", Language.get("en"))]),
            900,
            True,
            FontType.TRUETYPE,
            {"wght": 900.0},
        ),
    ]
    
    assert collections.Counter(fonts) == collections.Counter(expected_fonts)


def test_variable_font_with_invalid_elided_fallback_nameid():

    font_path = os.path.join(os.path.dirname(dir_path), "variable font tests", "Test #6", "Test #6.ttf")

    fonts = FactoryABCFont.from_font_path(font_path)
    expected_fonts = [
        VariableFont(
            font_path,
            0,
            set([Name("Advent Pro", Language.get("en"))]),
            set([Name("", Language.get("en"))]),
            set([Name("Regular", Language.get("en"))]),
            400,
            False,
            FontType.TRUETYPE,
            {'wdth': 100.0, 'wght': 100.0},
        )
    ]

    assert fonts == expected_fonts


def test_variable_font_match_with_axis_value_format_4_and_axis_format_1():
    # The NamedInstance "wght" == 800 will take the AxisValue Format 4 weight and the AxisValue Format 1 "ital".

    font_path = os.path.join(os.path.dirname(dir_path), "variable font tests", "Test #7", "Test #7.ttf")

    fonts = FactoryABCFont.from_font_path(font_path)
    expected_fonts = [
        VariableFont(
            font_path,
            0,
            set([Name("Alegreya", Language.get("en"))]),
            set([Name("", Language.get("en"))]),
            set([Name("Italic", Language.get("en"))]),
            400,
            True,
            FontType.TRUETYPE,
            {"wght": 400.0},
        ),
        VariableFont(
            font_path,
            0,
            set([Name("Alegreya", Language.get("en"))]),
            set([Name("Medium", Language.get("en"))]),
            set([Name("Medium Italic", Language.get("en"))]),
            500,
            True,
            FontType.TRUETYPE,
            {"wght": 500.0},
        ),
        VariableFont(
            font_path,
            0,
            set([Name("Alegreya", Language.get("en"))]),
            set([Name("", Language.get("en"))]),
            set([Name("Bold Italic", Language.get("en"))]),
            700,
            True,
            FontType.TRUETYPE,
            {"wght": 700.0},
        ),
        VariableFont(
            font_path,
            0,
            set([Name("Alegreya", Language.get("en"))]),
            set([Name("ExtraBold", Language.get("en"))]),
            set([Name("ExtraBold Italic", Language.get("en"))]),
            755,
            True,
            FontType.TRUETYPE,
            {"wght": 800.0},
        ),
        VariableFont(
            font_path,
            0,
            set([Name("Alegreya", Language.get("en"))]),
            set([Name("Black", Language.get("en"))]),
            set([Name("Black Italic", Language.get("en"))]),
            900,
            True,
            FontType.TRUETYPE,
            {"wght": 900.0},
        ),
    ]

    assert collections.Counter(fonts) == collections.Counter(expected_fonts)


def test_variable_font_duplicate_font_face():
    font_path = os.path.join(os.path.dirname(dir_path), "variable font tests", "Test #8", "Test #8.ttf")

    fonts = FactoryABCFont.from_font_path(font_path)
    expected_fonts = [
        VariableFont(
            font_path,
            0,
            set([Name("Alegreya", Language.get("en"))]),
            set([Name("", Language.get("en"))]),
            set([Name("Italic", Language.get("en"))]),
            400,
            True,
            FontType.TRUETYPE,
            {"wght": 400.0},
        ),
        VariableFont(
            font_path,
            0,
            set([Name("Alegreya", Language.get("en"))]),
            set([Name("Medium", Language.get("en"))]),
            set([Name("Medium Italic", Language.get("en"))]),
            500,
            True,
            FontType.TRUETYPE,
            {"wght": 500.0},
        ),
        VariableFont(
            font_path,
            0,
            set([Name("Alegreya", Language.get("en"))]),
            set([Name("", Language.get("en"))]),
            set([Name("Bold Italic", Language.get("en"))]),
            700,
            True,
            FontType.TRUETYPE,
            {"wght": 700.0},
        ),
        VariableFont(
            font_path,
            0,
            set([Name("Alegreya", Language.get("en"))]),
            set([Name("Black", Language.get("en"))]),
            set([Name("Black Italic", Language.get("en"))]),
            900,
            True,
            FontType.TRUETYPE,
            {"wght": 800.0},
        ),
    ]

    assert collections.Counter(fonts) == collections.Counter(expected_fonts)


def test_variable_font_with_multiple_lang_name_id():
    font_path = os.path.join(os.path.dirname(dir_path), "variable font tests", "Test #9", "Test #9.ttf")

    fonts = FactoryABCFont.from_font_path(font_path)
    expected_fonts = [
        VariableFont(
            font_path,
            0,
            set([Name("family text", Language.get("fr-CA"))]),
            set([Name("", Language.get("en")), Name("", Language.get("fr-CA"))]),
            set([Name("Italic", Language.get("en")), Name("Italic", Language.get("fr-CA"))]),
            400,
            True,
            FontType.TRUETYPE,
            {"wght": 400.0},
        ),
        VariableFont(
            font_path,
            0,
            set([Name("family text", Language.get("fr-CA"))]),
            set([Name("Medium", Language.get("en")), Name("Medium", Language.get("fr-CA")), Name("Medium French Canada", Language.get("fr-CA"))]),
            set([Name("Medium Italic", Language.get("en")), Name("Medium Italic", Language.get("fr-CA")), Name("Medium French Canada Italic", Language.get("fr-CA"))]),
            500,
            True,
            FontType.TRUETYPE,
            {"wght": 500.0},
        ),
        VariableFont(
            font_path,
            0,
            set([Name("family text", Language.get("fr-CA"))]),
            set([Name("", Language.get("en")), Name("", Language.get("fr-CA"))]),
            set([Name("Bold Italic", Language.get("en")), Name("Bold Italic", Language.get("fr-CA")), Name("Bold French Canada Italic", Language.get("fr-CA"))]),
            700,
            True,
            FontType.TRUETYPE,
            {"wght": 700.0},
        ),
        VariableFont(
            font_path,
            0,
            set([Name("family text", Language.get("fr-CA"))]),
            set([Name("ExtraBold", Language.get("fr-CA"))]),
            set([Name("ExtraBold Italic", Language.get("fr-CA"))]),
            800,
            True,
            FontType.TRUETYPE,
            {"wght": 800.0},
        ),
        VariableFont(
            font_path,
            0,
            set([Name("family text", Language.get("fr-CA"))]),
            set([Name("Black", Language.get("en")), Name("Black", Language.get("fr-CA")), Name("Black French Canada", Language.get("fr-CA"))]),
            set([Name("Black Italic", Language.get("en")), Name("Black Italic", Language.get("fr-CA")), Name("Black French Canada Italic", Language.get("fr-CA"))]),
            900,
            True,
            FontType.TRUETYPE,
            {"wght": 900.0},
        ),
    ]

    assert collections.Counter(fonts) == collections.Counter(expected_fonts)


def test_stat_invalid_axis_value_id():
    font_path = os.path.join(os.path.dirname(dir_path), "variable font tests", "Test #10", "Test #10.ttf")
    fonts = FactoryABCFont.from_font_path(font_path)


    expected_font = [Font(
        font_path, 
        0, 
        set([Name("Alegreya", Language.get("en"))]), 
        set([Name("Alegreya Italic", Language.get("en"))]),
        400, 
        True, 
        False, 
        FontType.TRUETYPE,
    )]

    assert fonts == expected_font


def test_without_ElidedFallbackNameID():
    font_path = os.path.join(os.path.dirname(dir_path), "variable font tests", "Test #11", "Test #11.ttf")
    fonts = FactoryABCFont.from_font_path(font_path)

    expected_fonts = [
        VariableFont(
            font_path, 
            0, 
            set([Name("Advent Pro", Language.get("en"))]), 
            set([Name("", Language.get("en"))]), 
            set([Name("Normal", Language.get("en"))]),
            100, 
            True, 
            FontType.TRUETYPE,
            {'wdth': 100.0, 'wght': 100.0},
        ),
        VariableFont(
            font_path, 
            0, 
            set([Name("Advent Pro", Language.get("en"))]), 
            set([Name("", Language.get("en"))]), 
            set([Name("Normal", Language.get("en"))]),
            200, 
            True, 
            FontType.TRUETYPE,
            {'wdth': 100.0, 'wght': 200.0},
        ),
        VariableFont(
            font_path, 
            0, 
            set([Name("Advent Pro", Language.get("en"))]), 
            set([Name("", Language.get("en"))]), 
            set([Name("Normal", Language.get("en"))]),
            300, 
            True, 
            FontType.TRUETYPE,
            {'wdth': 100.0, 'wght': 300.0},
        ),
        VariableFont(
            font_path, 
            0, 
            set([Name("Advent Pro", Language.get("en"))]), 
            set([Name("", Language.get("en"))]), 
            set([Name("Normal", Language.get("en"))]),
            400, 
            True, 
            FontType.TRUETYPE,
            {'wdth': 100.0, 'wght': 400.0},
        ),
        VariableFont(
            font_path, 
            0, 
            set([Name("Advent Pro", Language.get("en"))]), 
            set([Name("", Language.get("en"))]), 
            set([Name("Normal", Language.get("en"))]),
            500, 
            True, 
            FontType.TRUETYPE,
            {'wdth': 100.0, 'wght': 500.0},
        ),
        VariableFont(
            font_path, 
            0, 
            set([Name("Advent Pro", Language.get("en"))]), 
            set([Name("", Language.get("en"))]), 
            set([Name("Normal", Language.get("en"))]),
            600, 
            True, 
            FontType.TRUETYPE,
            {'wdth': 100.0, 'wght': 600.0},
        ),
        VariableFont(
            font_path, 
            0, 
            set([Name("Advent Pro", Language.get("en"))]), 
            set([Name("", Language.get("en"))]), 
            set([Name("Normal", Language.get("en"))]),
            700, 
            True, 
            FontType.TRUETYPE,
            {'wdth': 100.0, 'wght': 700.0},
        ),
        VariableFont(
            font_path, 
            0, 
            set([Name("Advent Pro", Language.get("en"))]), 
            set([Name("", Language.get("en"))]), 
            set([Name("Normal", Language.get("en"))]),
            800, 
            True, 
            FontType.TRUETYPE,
            {'wdth': 100.0, 'wght': 800.0},
        ),
        VariableFont(
            font_path, 
            0, 
            set([Name("Advent Pro", Language.get("en"))]), 
            set([Name("", Language.get("en"))]), 
            set([Name("Normal", Language.get("en"))]),
            900, 
            True, 
            FontType.TRUETYPE,
            {'wdth': 100.0, 'wght': 900.0},
        )
    ]

    assert collections.Counter(fonts) == collections.Counter(expected_fonts)


def test_variable_font_without_DesignAxisRecord():

    font_path = os.path.join(os.path.dirname(dir_path), "variable font tests", "Test #12", "Test #12.ttf")

    with pytest.raises(InvalidVariableFontException) as exc_info:
        FactoryABCFont.from_font_path(font_path)
    assert str(exc_info.value) == "The font has a stat table, but it doesn't have any DesignAxisRecord"


def test_variable_font_without_invalid_name_id():
    font_path = os.path.join(os.path.dirname(dir_path), "variable font tests", "Test #13", "Test #13.ttf")
    fonts = FactoryABCFont.from_font_path(font_path)

    expected_fonts = [
        Font(
            font_path, 
            0, 
            set([Name("Alegreya", Language.get("en"))]), 
            set([Name("Alegreya Italic", Language.get("en"))]), 
            400, 
            True,
            False,
            FontType.TRUETYPE,
        ),
    ]

    assert collections.Counter(fonts) == collections.Counter(expected_fonts)


def test_opentype_font():
    font_path = os.path.join(os.path.dirname(dir_path), "fonts", "PENBOX.otf")
    fonts = FactoryABCFont.from_font_path(font_path)

    expected_fonts = [
        Font(
            font_path, 
            0, 
            set([Name("PENBOX", Language.get("en"))]), 
            set([Name("PENBOXRegular", Language.get("en"))]), 
            400, 
            False,
            False,
            FontType.OPENTYPE,
        ),
    ]

    assert collections.Counter(fonts) == collections.Counter(expected_fonts)