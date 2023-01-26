import os
from font_collector import Font

dir_path = os.path.dirname(os.path.realpath(__file__))
font_without_os2_table = os.path.join(dir_path, "fonts", "BRUSHSTP.TTF")
font_without_stat_table = os.path.join(dir_path, "fonts", "Cabin VF Beta Regular.ttf")

def test_font_without_os2_table():

    font = Font.from_font_path(font_without_os2_table)
    assert len(font) == 1
    font = font[0]

    print(font)

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