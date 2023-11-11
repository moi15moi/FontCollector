import collections
import os
import pytest
import string
from font_collector import VariableFont, FontType, InvalidLanguageCode, Name
from langcodes import Language
from typing import Hashable

dir_path = os.path.dirname(os.path.realpath(__file__))


def test__init__():
    filename = "example"
    font_index = 0
    families_prefix = {Name("families_prefix", Language.get("en"))}
    families_suffix = {Name("families_suffix", Language.get("en"))}
    exact_names_suffix = {Name("exact_names_suffix", Language.get("en"))}
    weight = 400
    is_italic = False
    font_type = FontType.TRUETYPE
    named_instance_coordinates = {"ital": False}

    font = VariableFont(
        filename,
        font_index,
        families_prefix,
        families_suffix,
        exact_names_suffix,
        weight,
        is_italic,
        font_type,
        named_instance_coordinates
    )

    assert font.filename == filename
    assert font.font_index == font_index
    assert font.families_prefix == families_prefix
    assert font.families_suffix == families_suffix
    assert font.exact_names_suffix == exact_names_suffix
    assert font.weight == weight
    assert font.is_italic == is_italic
    assert font.named_instance_coordinates == named_instance_coordinates


def test_filename_property():
    font = VariableFont("example", 0, {}, {}, {}, 400, False, FontType.TRUETYPE, {})
    filename = "test"
    font.filename = filename
    assert font.filename == filename


def test_font_index_property():
    font = VariableFont("example", 0, {}, {}, {}, 400, False, FontType.TRUETYPE, {})
    font_index = 1
    font.font_index = font_index
    assert font.font_index == font_index


def test_families_prefix_property():
    font = VariableFont("example", 0, {}, {}, {}, 400, False, FontType.TRUETYPE, {})
    families_prefix = {Name("test", Language.get("en"))}
    font.families_prefix = families_prefix
    assert font.families_prefix == families_prefix


def test_families_suffix_property():
    font = VariableFont("example", 0, {}, {}, {}, 400, False, FontType.TRUETYPE, {})
    families_suffix = {Name("test", Language.get("en"))}
    font.families_suffix = families_suffix
    assert font.families_suffix == families_suffix


def test_family_names_property():
    font = VariableFont("example", 0, {}, {}, {}, 400, False, FontType.TRUETYPE, {})
    with pytest.raises(AttributeError) as exc_info:
        font.family_names = ""
    assert str(exc_info.value) == "You cannot set the family name for an variable font. You need to set the families_prefix or the families_suffix."

    assert font.family_names == set()

    font.families_prefix = {Name("family", Language.get("fr-CA"))}
    font.families_suffix = {Name("suffix name", Language.get("en"))}
    assert font.family_names == {Name("family suffix name", Language.get("en"))}

    font.families_prefix = {Name("family", Language.get("fr-CA")), Name("family 2", Language.get("fr-CA"))}
    assert font.family_names == {Name("family 2 suffix name", Language.get("en")), Name("family suffix name", Language.get("en"))}

    font.families_suffix = {Name("suffix name", Language.get("en")), Name("suffix name 2", Language.get("es"))}
    assert font.family_names == {
        Name("family 2 suffix name", Language.get("en")),
        Name("family suffix name", Language.get("en")),
        Name("family 2 suffix name 2", Language.get("es")),
        Name("family suffix name 2", Language.get("es"))
    }


def test_exact_names_suffix_property():
    font = VariableFont("example", 0, {}, {}, {}, 400, False, FontType.TRUETYPE, {})
    exact_names_suffix = {Name("test", Language.get("en"))}
    font.exact_names_suffix = exact_names_suffix
    assert font.exact_names_suffix == exact_names_suffix


def test_exact_names_property():
    font = VariableFont("example", 0, {}, {}, {}, 400, False, FontType.TRUETYPE, {})
    with pytest.raises(AttributeError) as exc_info:
        font.exact_names = ""
    assert str(exc_info.value) == "You cannot set the exact name for an variable font. You need to set the families_prefix or the exact_names_suffix."

    assert font.exact_names == set()

    font.families_prefix = {Name("family", Language.get("fr-CA"))}
    font.exact_names_suffix = {Name("exact name", Language.get("en"))}
    assert font.exact_names == {Name("family exact name", Language.get("en"))}

    font.families_prefix = {Name("family", Language.get("fr-CA")), Name("family 2", Language.get("fr-CA"))}
    assert font.exact_names == {Name("family 2 exact name", Language.get("en")), Name("family exact name", Language.get("en"))}

    font.exact_names_suffix = {Name("exact name", Language.get("en")), Name("exact name 2", Language.get("es"))}
    assert font.exact_names == {
        Name("family 2 exact name", Language.get("en")),
        Name("family exact name", Language.get("en")),
        Name("family 2 exact name 2", Language.get("es")),
        Name("family exact name 2", Language.get("es"))
    }


def test_weight_property():
    font = VariableFont("example", 0, {}, {}, {}, 400, False, FontType.TRUETYPE, {})
    weight = 900
    font.weight = weight
    assert font.weight == weight


def test_is_italic_property():
    font = VariableFont("example", 0, {}, {}, {}, 400, False, FontType.TRUETYPE, {})
    is_italic = True
    font.is_italic = is_italic
    assert font.is_italic == is_italic


def test_is_glyph_emboldened_property():
    font = VariableFont("example", 0, {}, {}, {}, 400, False, FontType.TRUETYPE, {})
    with pytest.raises(AttributeError) as exc_info:
        font.is_glyph_emboldened = ""
    assert str(exc_info.value) == "You cannot set is_glyph_emboldened for an variable font. You need to change the weight."

    assert not font.is_glyph_emboldened

    font.weight = 401
    assert font.is_glyph_emboldened


def test_font_type_property():
    font = VariableFont("example", 0, {}, {}, {}, 400, False, FontType.TRUETYPE, {})
    font_type = FontType.OPENTYPE
    font.font_type = font_type
    assert font.font_type == font_type


def test_named_instance_coordinates_property():
    font = VariableFont("example", 0, {}, {}, {}, 400, False, FontType.TRUETYPE, {})
    named_instance_coordinates = {"wght": 800}
    font.named_instance_coordinates = named_instance_coordinates
    assert font.named_instance_coordinates == named_instance_coordinates


def test_get_missing_glyphs():
    font_path = os.path.join(os.path.dirname(dir_path), "fonts", "Asap-VariableFont_wdth,wght.ttf")
    font = VariableFont(
        font_path,
        0,
        {},
        {},
        {},
        400,
        False,
        FontType.TRUETYPE,
        {}
    )

    missing_glyphs = font.get_missing_glyphs(string.ascii_letters + string.digits + "éｦ&*╠" )
    assert missing_glyphs == {"ｦ", "╠"}


def test__eq__():
    font_1 = VariableFont(
        "example",
        0,
        {Name("families_prefix", Language.get("fr"))},
        {Name("families_suffix", Language.get("fr"))},
        {Name("exact_names_suffix", Language.get("fr"))},
        400,
        False,
        FontType.TRUETYPE,
        {"ital": False}
    )
    assert font_1 == font_1

    font_2 = VariableFont(
        "example",
        0,
        {Name("families_prefix", Language.get("fr"))},
        {Name("families_suffix", Language.get("fr"))},
        {Name("exact_names_suffix", Language.get("fr"))},
        400,
        False,
        FontType.TRUETYPE,
        {"ital": False}
    )
    assert font_1 == font_2

    font_3 = VariableFont(
        "example different", # different
        0,
        {Name("families_prefix", Language.get("fr"))},
        {Name("families_suffix", Language.get("fr"))},
        {Name("exact_names_suffix", Language.get("fr"))},
        400,
        False,
        FontType.TRUETYPE,
        {"ital": False}
    )
    assert font_1 != font_3

    font_4 = VariableFont(
        "example",
        1, # different
        {Name("families_prefix", Language.get("fr"))},
        {Name("families_suffix", Language.get("fr"))},
        {Name("exact_names_suffix", Language.get("fr"))},
        400,
        False,
        FontType.TRUETYPE,
        {"ital": False}
    )
    assert font_1 != font_4

    font_5 = VariableFont(
        "example",
        0,
        {Name("families_prefix different", Language.get("fr"))}, # different
        {Name("families_suffix", Language.get("fr"))},
        {Name("exact_names_suffix", Language.get("fr"))},
        400,
        False,
        FontType.TRUETYPE,
        {"ital": False}
    )
    assert font_1 != font_5

    font_6 = VariableFont(
        "example",
        0,
        {Name("families_prefix", Language.get("fr"))},
        {Name("families_suffix different", Language.get("fr"))}, # different
        {Name("exact_names_suffix", Language.get("fr"))},
        400,
        False,
        FontType.TRUETYPE,
        {"ital": False}
    )
    assert font_1 != font_6

    font_7 = VariableFont(
        "example",
        0,
        {Name("families_prefix", Language.get("fr"))},
        {Name("families_suffix", Language.get("fr"))},  
        {Name("exact_names_suffix different", Language.get("fr"))}, # different
        400,
        False,
        FontType.TRUETYPE,
        {"ital": False}
    )
    assert font_1 != font_7

    font_8 = VariableFont(
        "example",
        0,
        {Name("families_prefix", Language.get("fr"))},
        {Name("families_suffix", Language.get("fr"))},  
        {Name("exact_names_suffix", Language.get("fr"))},
        401, # different
        False,
        FontType.TRUETYPE,
        {"ital": False}
    )
    assert font_1 != font_8

    font_9 = VariableFont(
        "example",
        0,
        {Name("families_prefix", Language.get("fr"))},
        {Name("families_suffix", Language.get("fr"))},  
        {Name("exact_names_suffix", Language.get("fr"))},
        400, 
        True, # different
        FontType.TRUETYPE,
        {"ital": False}
    )
    assert font_1 != font_9

    font_10 = VariableFont(
        "example",
        0,
        {Name("families_prefix", Language.get("fr"))},
        {Name("families_suffix", Language.get("fr"))},  
        {Name("exact_names_suffix", Language.get("fr"))},
        400, 
        False, 
        FontType.OPENTYPE, # different
        {"ital": False}
    )
    assert font_1 != font_10

    font_11 = VariableFont(
        "example",
        0,
        {Name("families_prefix", Language.get("fr"))},
        {Name("families_suffix", Language.get("fr"))},  
        {Name("exact_names_suffix", Language.get("fr"))},
        400, 
        False, 
        FontType.TRUETYPE, 
        {"ital": True} # different
    )
    assert font_1 != font_11

    font_12 = VariableFont(
        "example",
        0,
        {Name("families_prefix", Language.get("fr"))},
        {Name("families_suffix", Language.get("fr"))},  
        {Name("exact_names_suffix", Language.get("fr"))},
        400, 
        False, 
        FontType.TRUETYPE, 
        {"ital different": False} # different
    )
    assert font_1 != font_12


def test__hash__():
    font = VariableFont(
        "example",
        0,
        {Name("families_prefix", Language.get("fr"))},
        {Name("families_suffix", Language.get("fr"))},  
        {Name("exact_names_suffix", Language.get("fr"))},
        400, 
        False, 
        FontType.TRUETYPE, 
        {"ital": False}
    )

    assert isinstance(font, Hashable)

    font_1 = VariableFont(
        "example",
        0,
        {Name("families_prefix", Language.get("fr"))},
        {Name("families_suffix", Language.get("fr"))},
        {Name("exact_names_suffix", Language.get("fr"))},
        400,
        False,
        FontType.TRUETYPE,
        {"ital": False, "wght": 400}
    )
    assert font_1 == font_1

    font_2 = VariableFont(
        "example",
        0,
        {Name("families_prefix", Language.get("fr"))},
        {Name("families_suffix", Language.get("fr"))},
        {Name("exact_names_suffix", Language.get("fr"))},
        400,
        False,
        FontType.TRUETYPE,
        {"wght": 400, "ital": False}
    )
    assert {font_1} == {font_2}


def test__repr__():
    font = VariableFont(
        "example",
        0,
        {Name("families_prefix", Language.get("fr"))},
        {Name("families_suffix", Language.get("fr"))},  
        {Name("exact_names_suffix", Language.get("fr"))},
        400, 
        False, 
        FontType.TRUETYPE, 
        {"ital": False}
    )

    assert repr(font) == 'VariableFont(Filename="example", Font index="0", Family_names="{Name(value="families_prefix families_suffix", lang_code="fr")}", Exact_names="{Name(value="families_prefix exact_names_suffix", lang_code="fr")}", Weight="400", Italic="False", Glyph emboldened="False", Font type="TRUETYPE", Named instance coordinates="{\'ital\': False}")'