from collections.abc import Hashable
from font_collector import AssStyle


def test__init__():
    fontname = "Test"
    weight = 700
    italic = False
    ass_style = AssStyle(fontname, weight, italic)

    assert ass_style.fontname == fontname
    assert ass_style.weight == weight
    assert ass_style.italic == italic


def test_strip_fontname():
    fontname = "@Test"
    fontname_strip = AssStyle.strip_fontname(fontname)
    assert fontname_strip == "Test"

    # It should only remove @ when it is the first character
    fontname = "l@Test"
    fontname_strip = AssStyle.strip_fontname(fontname)
    assert fontname_strip == "l@Test"


def test_fontname_property():
    fontname = "Example"
    weight = 700
    italic = False
    ass_style = AssStyle(fontname, weight, italic)

    fontname = "@Test"
    ass_style.fontname = fontname
    assert ass_style.fontname == "Test"


def test__eq__():
    ass_style_1 = AssStyle(
        "Test",
        700,
        False
    )
    ass_style_2 = AssStyle(
        "test", # Different
        700,
        False
    )
    assert ass_style_1 == ass_style_2


    ass_style_3 = AssStyle(
        "Test",
        800, # Different
        False
    )
    assert ass_style_1 != ass_style_3

    ass_style_4 = AssStyle(
        "Test",
        700,
        True # Different
    )

    assert ass_style_1 != ass_style_4

    assert ass_style_1 != "test"


def test__hash__():
    ass_style_1 = AssStyle(
        "Test",
        700,
        False
    )
    ass_style_2 = AssStyle(
        "test", # Different
        700,
        False
    )
    assert isinstance(ass_style_1, Hashable)
    assert {ass_style_1} == {ass_style_2}


    ass_style_3 = AssStyle(
        "Test",
        800, # Different
        False
    )
    assert {ass_style_1} != {ass_style_3}

    ass_style_4 = AssStyle(
        "Test",
        700,
        True # Different
    )

    assert {ass_style_1} != {ass_style_4}

    assert {ass_style_1} != "test"


def test__repr__():
    fontname = "Example"
    weight = 700
    italic = False
    ass_style = AssStyle(fontname, weight, italic)

    assert repr(ass_style) == 'AssStyle(Font name="Example", Weight="700", Italic="False")'
