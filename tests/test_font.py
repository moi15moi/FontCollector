import os
import string
from font_collector import Font

dir_path = os.path.dirname(os.path.realpath(__file__))
font_without_os2_table = os.path.join(dir_path, "fonts", "font_mac.TTF")
font_without_axis_value = os.path.join(dir_path, "fonts", "font_without axis_value.ttf")


def test_font_without_os2_table():

    font = Font.from_font_path(font_without_os2_table)
    assert len(font) == 1
    font = font[0]

    assert font.family_names == set(["brushstroke plain"])
    assert font.weight == 400
    assert font.italic == False
    assert font.exact_names == set()
    assert font.is_var == False


def test_font_with_fvar_table_but_without_stat_table():

    font_without_stat_table = os.path.join(
        dir_path, "fonts", "Cabin VF Beta Regular.ttf"
    )

    font = Font.from_font_path(font_without_stat_table)
    assert len(font) == 1
    font = font[0]

    assert font.family_names == set(["cabin vf beta"])
    assert font.weight == 400
    assert font.italic == False
    assert font.exact_names == set(["cabin vf beta regular"])
    assert font.is_var == False


def test_font_without_axis_value():
    fonts = Font.from_font_path(font_without_axis_value)
    expected_fonts = [
        Font(
            font_without_axis_value,
            0,
            ["inter"],
            400,
            False,
            ["inter regular"],
            {"wght": 100.0, "slnt": 0.0},
        )
    ] * 18
    assert fonts == expected_fonts


def test_font_get_missing_glyphs_cmap_encoding_0():

    font_cmap_encoding_0 = os.path.join(dir_path, "fonts", "font_cmap_encoding_0.ttf")

    font = Font.from_font_path(font_cmap_encoding_0)
    assert len(font) == 1
    font = font[0]

    # Verify is the optional param is the right value
    missing_glyphs = font.get_missing_glyphs("Έκθεση για Απασχόληση Dream Top Co. Οι επιλογές À a")
    assert missing_glyphs == set("À")

    missing_glyphs = font.get_missing_glyphs("Έκθεση για Απασχόληση Dream Top Co. Οι επιλογές À a", False)
    assert missing_glyphs == set("À")

    missing_glyphs = font.get_missing_glyphs("Έκθεση για Απασχόληση Dream Top Co. Οι επιλογές À a", True)
    assert missing_glyphs == set("ΈκθεσηγιαπασχόλησηΟιεπιλογέςÀΑ")


def test_font_get_missing_glyphs_cmap_encoding_1():

    font_cmap_encoding_1 = os.path.join(dir_path, "fonts", "font_cmap_encoding_1.TTF")

    font = Font.from_font_path(font_cmap_encoding_1)
    assert len(font) == 1
    font = font[0]

    missing_glyphs = font.get_missing_glyphs(string.digits + "🇦🤍")
    assert missing_glyphs == set()


def test_font_get_missing_glyphs_cmap_encoding_2():

    font_cmap_encoding_2 = os.path.join(dir_path, "fonts", "font_cmap_encoding_2.TTF")

    font = Font.from_font_path(font_cmap_encoding_2)
    assert len(font) == 1
    font = font[0]

    missing_glyphs = font.get_missing_glyphs(
        string.ascii_letters + string.digits + "éｦ&*"
    )
    assert missing_glyphs == set(["é"])


def test_font_get_missing_glyphs_cmap_encoding_mac_platform():

    font = Font.from_font_path(font_without_os2_table)
    assert len(font) == 1
    font = font[0]

    missing_glyphs = font.get_missing_glyphs(
        string.ascii_letters + string.digits + "@é¸"
    )
    assert missing_glyphs == set(["@", "¸"])


def test_variable_font_with_invalid_fvar_axes():

    font_path = os.path.join(dir_path, "variable font tests", "Test #1", "Test #1.ttf")

    font = Font.from_font_path(font_path)
    assert len(font) == 1
    font = font[0]

    expected_font = Font(font_path, 0, ["Advent Pro"], 400, True, ["Advent Pro Italic"])

    assert font == expected_font


def test_variable_font_without_fvar_table():

    font_path = os.path.join(dir_path, "variable font tests", "Test #3", "Test #3.ttf")

    font = Font.from_font_path(font_path)
    assert len(font) == 1
    font = font[0]

    expected_font = Font(font_path, 0, ["Advent Pro"], 300, True, ["Advent Pro Italic"])

    assert font == expected_font


def test_variable_font_with_axis_value_format_4_one_axis_value_record():
    # The AxisValue Format 4 contain only 1 AxisValue in the AxisValueRecord

    font_path = os.path.join(dir_path, "variable font tests", "Test #4", "Test #4.ttf")

    fonts = Font.from_font_path(font_path)
    expected_fonts = [
        Font(
            font_path, 0, ["Alegreya"], 400, True, ["Alegreya Italic"], {"wght": 400.0}
        ),
        Font(
            font_path,
            0,
            ["Alegreya Medium"],
            500,
            True,
            ["Alegreya Medium Italic"],
            {"wght": 500.0},
        ),
        Font(
            font_path,
            0,
            ["Alegreya"],
            700,
            True,
            ["Alegreya Bold Italic"],
            {"wght": 700.0},
        ),
        Font(
            font_path,
            0,
            ["Alegreya Roman numerals"],
            800,
            True,
            ["Alegreya Roman numerals Italic"],
            {"wght": 800.0},
        ),
        Font(
            font_path,
            0,
            ["Alegreya Black"],
            900,
            True,
            ["Alegreya Black Italic"],
            {"wght": 900.0},
        ),
    ]

    assert fonts == expected_fonts


def test_variable_font_with_axis_value_format_4_multiple_axis_value_record():
    # The AxisValue Format 4 contain multiple AxisValue in the AxisValueRecord

    font_path = os.path.join(dir_path, "variable font tests", "Test #5", "Test #5.ttf")

    fonts = Font.from_font_path(font_path)
    expected_fonts = [
        Font(
            font_path, 0, ["Alegreya"], 400, True, ["Alegreya Italic"], {"wght": 400.0}
        ),
        Font(
            font_path,
            0,
            ["Alegreya Medium"],
            500,
            True,
            ["Alegreya Medium Italic"],
            {"wght": 500.0},
        ),
        Font(
            font_path,
            0,
            ["Alegreya"],
            700,
            True,
            ["Alegreya Bold Italic"],
            {"wght": 700.0},
        ),
        Font(
            font_path,
            0,
            ["Alegreya Roman numerals"],
            400,
            False,
            ["Alegreya Roman numerals"],
            {"wght": 400.0},
        ),
        Font(
            font_path,
            0,
            ["Alegreya Black"],
            900,
            True,
            ["Alegreya Black Italic"],
            {"wght": 900.0},
        ),
    ]

    assert fonts == expected_fonts


def test_variable_font_with_invalid_elided_fallback_nameid():

    font_path = os.path.join(dir_path, "variable font tests", "Test #6", "Test #6.ttf")

    fonts = Font.from_font_path(font_path)
    expected_fonts = [
        Font(
            font_path,
            0,
            ["Advent Pro"],
            400,
            False,
            ["Advent Pro Regular"],
            {"wght": 400.0},
        )
    ] * 9

    assert fonts == expected_fonts


def test_variable_font_match_with_axis_value_format_4_and_axis_format_1():
    # The NamedInstance "wght" == 800 will take the AxisValue Format 4 weight and the AxisValue Format 1 "ital".

    font_path = os.path.join(dir_path, "variable font tests", "Test #7", "Test #7.ttf")

    fonts = Font.from_font_path(font_path)
    expected_fonts = [
        Font(
            font_path, 0, ["Alegreya"], 400, True, ["Alegreya Italic"], {"wght": 400.0}
        ),
        Font(
            font_path,
            0,
            ["Alegreya Medium"],
            500,
            True,
            ["Alegreya Medium Italic"],
            {"wght": 500.0},
        ),
        Font(
            font_path,
            0,
            ["Alegreya"],
            700,
            True,
            ["Alegreya Bold Italic"],
            {"wght": 700.0},
        ),
        Font(
            font_path,
            0,
            ["Alegreya ExtraBold"],
            755,
            True,
            ["Alegreya ExtraBold Italic"],
            {"wght": 800.0},
        ),
        Font(
            font_path,
            0,
            ["Alegreya Black"],
            900,
            True,
            ["Alegreya Black Italic"],
            {"wght": 900.0},
        ),
    ]

    assert fonts == expected_fonts


def test_variable_font_duplicate_font_face():

    font_path = os.path.join(dir_path, "variable font tests", "Test #8", "Test #8.ttf")

    fonts = Font.from_font_path(font_path)
    expected_fonts = [
        Font(
            font_path, 0, ["Alegreya"], 400, True, ["Alegreya Italic"], {"wght": 400.0}
        ),
        Font(
            font_path,
            0,
            ["Alegreya Medium"],
            500,
            True,
            ["Alegreya Medium Italic"],
            {"wght": 500.0},
        ),
        Font(
            font_path,
            0,
            ["Alegreya"],
            700,
            True,
            ["Alegreya Bold Italic"],
            {"wght": 700.0},
        ),
        Font(
            font_path,
            0,
            ["Alegreya Black"],
            900,
            True,
            ["Alegreya Black Italic"],
            {"wght": 900.0},
        ),
        Font(
            font_path,
            0,
            ["Alegreya Black"],
            900,
            True,
            ["Alegreya Black Italic"],
            {"wght": 900.0},
        ),
    ]

    assert fonts == expected_fonts
