import os
from font_collector.font_parser import FontParser
from fontTools.ttLib.ttFont import TTFont

dir_path = os.path.dirname(os.path.realpath(__file__))
variable_font = TTFont(os.path.join(dir_path, "fonts", "bahnschrift (original).ttf"))


def test_get_var_font_family_prefix():

    assert "Bahnschrift" == FontParser.get_var_font_family_prefix(variable_font)


def test_get_var_font_family_fullname():
    families = []
    fullname = []

    for instance in variable_font["fvar"].instances:
        axis_value_tables = FontParser.get_axis_value_from_coordinates(
            variable_font, instance.coordinates
        )

        family_name, full_font_name = FontParser.get_var_font_family_fullname(
            variable_font, axis_value_tables
        )

        families.append(family_name)
        fullname.append(full_font_name)

    expected_families = [
        "Bahnschrift Light",
        "Bahnschrift SemiLight",
        "Bahnschrift",
        "Bahnschrift SemiBold",
        "Bahnschrift",
        "Bahnschrift Light SemiCondensed",
        "Bahnschrift SemiLight SemiCondensed",
        "Bahnschrift SemiCondensed",
        "Bahnschrift SemiBold SemiCondensed",
        "Bahnschrift SemiCondensed",
        "Bahnschrift Light Condensed",
        "Bahnschrift SemiLight Condensed",
        "Bahnschrift Condensed",
        "Bahnschrift SemiBold Condensed",
        "Bahnschrift Condensed",
    ]
    expected_fullname = [
        "Bahnschrift Light",
        "Bahnschrift SemiLight",
        "Bahnschrift Regular",
        "Bahnschrift SemiBold",
        "Bahnschrift Bold",
        "Bahnschrift Light SemiCondensed",
        "Bahnschrift SemiLight SemiCondensed",
        "Bahnschrift SemiCondensed",
        "Bahnschrift SemiBold SemiCondensed",
        "Bahnschrift Bold SemiCondensed",
        "Bahnschrift Light Condensed",
        "Bahnschrift SemiLight Condensed",
        "Bahnschrift Condensed",
        "Bahnschrift SemiBold Condensed",
        "Bahnschrift Bold Condensed",
    ]

    assert set(families) == set(expected_families)
    assert set(fullname) == set(expected_fullname)
