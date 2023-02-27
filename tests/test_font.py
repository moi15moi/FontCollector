import os
import string
from font_collector import Font

dir_path = os.path.dirname(os.path.realpath(__file__))
font_without_os2_table = os.path.join(dir_path, "fonts", "font_mac.TTF")
font_without_stat_table = os.path.join(dir_path, "fonts", "Cabin VF Beta Regular.ttf")
font_without_axis_value = os.path.join(dir_path, "fonts", "font_without axis_value.ttf")
font_cmap_encoding_2 = os.path.join(dir_path, "fonts", "font_cmap_encoding_2.TTF")


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

    font = Font.from_font_path(font_without_stat_table)
    assert len(font) == 1
    font = font[0]

    assert font.family_names == set(["cabin vf beta"])
    assert font.weight == 400
    assert font.italic == False
    assert font.exact_names == set(["cabin vf beta regular"])
    assert font.is_var == False


def test_font_without_axis_value():

    font = Font.from_font_path(font_without_axis_value)
    assert len(font) == 1
    font = font[0]

    assert font.family_names == set(["inter", "inter regular"])
    # I don't know which weight gdi take. It maybe takes the DefaultValue from the AxisTag=wght in the fvar table
    assert font.weight == 400
    assert font.italic == False
    assert font.exact_names == set([])
    assert font.is_var == True

def test_font_get_missing_glyphs_cmap_encoding_2():

    font = Font.from_font_path(font_cmap_encoding_2)
    assert len(font) == 1
    font = font[0]

    missing_glyphs = font.get_missing_glyphs(string.ascii_letters + string.digits + "éｦ&*")
    assert missing_glyphs == set(["é"])

def test_font_get_missing_glyphs_cmap_encoding_mac_platform():

    font = Font.from_font_path(font_without_os2_table)
    assert len(font) == 1
    font = font[0]

    missing_glyphs = font.get_missing_glyphs(string.ascii_letters + string.digits + "@é¸")
    assert missing_glyphs == set(["@", "¸"])
