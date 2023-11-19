import collections
import os
import pytest
import string
from font_collector import Font, FontType, InvalidLanguageCode, Name
from langcodes import Language
from typing import Hashable

dir_path = os.path.dirname(os.path.realpath(__file__))


def test__init__():
    filename = "example"
    font_index = 0
    family_names = [Name("family_names", Language.get("en"))]
    exact_names = [Name("exact_names", Language.get("en"))]
    weight = 400
    is_italic = False
    is_glyph_emboldened = False
    font_type = FontType.TRUETYPE

    font = Font(
        filename,
        font_index,
        family_names,
        exact_names,
        weight,
        is_italic,
        is_glyph_emboldened,
        font_type
    )

    assert font.filename == filename
    assert font.font_index == font_index
    assert font.family_names == family_names
    assert font.exact_names == exact_names
    assert font.weight == weight
    assert font.is_italic == is_italic
    assert font.is_glyph_emboldened == is_glyph_emboldened
    assert font.font_type == font_type


def test_filename_property():
    font = Font("example", 0, [], [], 400, False, False, FontType.TRUETYPE)
    filename = "test"
    font.filename = filename
    assert font.filename == filename


def test_font_index_property():
    font = Font("example", 0, [], [], 400, False, False, FontType.TRUETYPE)
    font_index = 1
    font.font_index = font_index
    assert font.font_index == font_index


def test_family_names_property():
    font = Font("example", 0, [], [], 400, False, False, FontType.TRUETYPE)
    family_names = [Name("test", Language.get("en"))]
    font.family_names = family_names
    assert font.family_names == family_names


def test_exact_names_property():
    font = Font("example", 0, [], [], 400, False, False, FontType.TRUETYPE)
    exact_names = [Name("test", Language.get("en"))]
    font.exact_names = exact_names
    assert font.exact_names == exact_names


def test_weight_property():
    font = Font("example", 0, [], [], 400, False, False, FontType.TRUETYPE)
    weight = 900
    font.weight = weight
    assert font.weight == weight


def test_is_italic_property():
    font = Font("example", 0, [], [], 400, False, False, FontType.TRUETYPE)
    is_italic = True
    font.is_italic = is_italic
    assert font.is_italic == is_italic


def test_is_glyph_emboldened_property():
    font = Font("example", 0, [], [], 400, False, False, FontType.TRUETYPE)
    is_glyph_emboldened = True
    font.is_glyph_emboldened = is_glyph_emboldened
    assert font.is_glyph_emboldened == is_glyph_emboldened


def test_font_type():
    font = Font("example", 0, [], [], 400, False, False, FontType.TRUETYPE)
    font_type = FontType.OPENTYPE
    font.font_type = font_type
    assert font.font_type == font_type


def test_font_get_missing_glyphs_cmap_encoding_0():
    font_cmap_encoding_0 = os.path.join(os.path.dirname(dir_path), "fonts", "font_cmap_encoding_0.TTF")
    font = Font(
        font_cmap_encoding_0,
        0,
        [],
        [],
        400,
        False,
        False,
        FontType.TRUETYPE
    )

    # Verify is the optional param is the right value
    missing_glyphs = font.get_missing_glyphs("Έκθεση για Απασχόληση Dream Top Co. Οι επιλογές À a")
    assert missing_glyphs == set("À")

    missing_glyphs = font.get_missing_glyphs("Έκθεση για Απασχόληση Dream Top Co. Οι επιλογές À a", False)
    assert missing_glyphs == set("À")

    missing_glyphs = font.get_missing_glyphs("Έκθεση για Απασχόληση Dream Top Co. Οι επιλογές À a", True)
    assert missing_glyphs == set("ΈκθεσηγιαπασχόλησηΟιεπιλογέςÀΑ")


def test_font_get_missing_glyphs_cmap_encoding_1():
    font_cmap_encoding_1 = os.path.join(os.path.dirname(dir_path), "fonts", "font_cmap_encoding_1.TTF")
    font = Font(
        font_cmap_encoding_1,
        0,
        [],
        [],
        400,
        False,
        False,
        FontType.TRUETYPE
    )

    missing_glyphs = font.get_missing_glyphs(string.digits + "🇦🤍")
    assert missing_glyphs == set()


def test_font_get_missing_glyphs_cmap_encoding_2():
    font_cmap_encoding_2 = os.path.join(os.path.dirname(dir_path), "fonts", "font_cmap_encoding_2.TTF")
    font = Font(
        font_cmap_encoding_2,
        0,
        [],
        [],
        400,
        False,
        False,
        FontType.TRUETYPE
    )

    # Try "é" since cp932 doesn't support this char
    missing_glyphs = font.get_missing_glyphs(
        string.ascii_letters + string.digits + "éｦ&*"
    )
    assert missing_glyphs == set(["é"])


def test_font_get_missing_glyphs_cmap_encoding_mac_platform():
    font_mac_platform = os.path.join(os.path.dirname(dir_path), "fonts", "font_mac.TTF")
    font = Font(
        font_mac_platform,
        0,
        [],
        [],
        400,
        False,
        False,
        FontType.TRUETYPE
    )

    missing_glyphs = font.get_missing_glyphs(string.ascii_letters + string.digits + "@é¸^Æ~")
    assert missing_glyphs == set(["@", "¸", "~"])


def test_get_family_and_exact_from_lang():
    font_path = "example"
    font_index = 0
    weight = 400
    italic = True
    is_glyph_emboldened = False
    font_type = FontType.TRUETYPE


    name_1 = Name("", Language.get("fr")) 
    name_2 = Name("", Language.get("fr-CA")) 
    name_3 = Name("", Language.get("fr-BE")) 

    family_names = [name_1, name_2, name_3]
    exact_names = set()

    font = Font(
        font_path,
        font_index,
        family_names,
        exact_names,
        weight,
        italic,
        is_glyph_emboldened,
        font_type
    )

    # lang_code where the language match
    assert font.get_family_from_lang("fr", exact_match=True) == [name_1]
    assert font.get_family_from_lang("fr")[0] == name_1
    assert collections.Counter(font.get_family_from_lang("fr")) == collections.Counter([name_1, name_2, name_3])
    
    # lang_code where the language and the territory match
    assert font.get_family_from_lang("fr-CA", exact_match=True) == [name_2]
    assert font.get_family_from_lang("fr-CA") == [name_2, name_1, name_3]

    # lang_code where the territory doesn't match
    assert font.get_family_from_lang("fr-US", exact_match=True) == []
    assert font.get_family_from_lang("fr-US")[0] == name_1
    assert collections.Counter(font.get_family_from_lang("fr-US")) == collections.Counter([name_1, name_2, name_3])

    # lang_code where the language doesn't match
    assert font.get_family_from_lang("en", exact_match=True) == []
    assert font.get_family_from_lang("en") == []

    # lang_code is invalid
    with pytest.raises(InvalidLanguageCode) as exc_info:
        font.get_family_from_lang("example")
    assert str(exc_info.value) == "The \"example\" does not conform to IETF BCP-47"


    # ----- Same test with exact_names -----
    font.exact_names = family_names
    font.family_names = set()

    assert font.get_exact_name_from_lang("fr", exact_match=True) == [name_1]
    assert font.get_exact_name_from_lang("fr")[0] == name_1
    assert collections.Counter(font.get_exact_name_from_lang("fr")) == collections.Counter([name_1, name_2, name_3])
    
    # lang_code where the language and the territory match
    assert font.get_exact_name_from_lang("fr-CA", exact_match=True) == [name_2]
    assert font.get_exact_name_from_lang("fr-CA") == [name_2, name_1, name_3]

    # lang_code where the territory doesn't match
    assert font.get_exact_name_from_lang("fr-US", exact_match=True) == []
    assert font.get_exact_name_from_lang("fr-US")[0] == name_1
    assert collections.Counter(font.get_exact_name_from_lang("fr-US")) == collections.Counter([name_1, name_2, name_3])

    # lang_code where the language doesn't match
    assert font.get_exact_name_from_lang("en", exact_match=True) == []
    assert font.get_exact_name_from_lang("en") == []

    # lang_code is invalid
    with pytest.raises(InvalidLanguageCode) as exc_info:
        font.get_exact_name_from_lang("example")
    assert str(exc_info.value) == "The \"example\" does not conform to IETF BCP-47"


def test__eq__():
    font_1 = Font(
        "example",
        0,
        [Name("family_names", Language.get("fr"))],
        [Name("exact_names", Language.get("fr"))],
        400,
        False,
        False,
        FontType.TRUETYPE
    )
    assert font_1 == font_1

    font_2 = Font(
        "example",
        0,
        [Name("family_names", Language.get("fr"))],
        [Name("exact_names", Language.get("fr"))],
        400,
        False,
        False,
        FontType.TRUETYPE
    )
    assert font_1 == font_2

    font_3 = Font(
        "example different", # different
        0,
        [Name("family_names", Language.get("fr"))],
        [Name("exact_names", Language.get("fr"))],
        400,
        False,
        False,
        FontType.TRUETYPE
    )
    assert font_1 != font_3

    font_4 = Font(
        "example",
        1, # different
        [Name("family_names", Language.get("fr"))],
        [Name("exact_names", Language.get("fr"))],
        400,
        False,
        False,
        FontType.TRUETYPE
    )
    assert font_1 != font_4

    font_5 = Font(
        "example",
        0,
        [Name("family_names different", Language.get("fr"))], # different
        [Name("exact_names", Language.get("fr"))],
        400,
        False,
        False,
        FontType.TRUETYPE
    )
    assert font_1 != font_5

    font_6 = Font(
        "example",
        0,
        [Name("family_names", Language.get("fr"))],
        [Name("exact_names different", Language.get("fr"))], # different
        400,
        False,
        False,
        FontType.TRUETYPE
    )
    assert font_1 != font_6

    font_7 = Font(
        "example",
        0,
        [Name("family_names", Language.get("fr"))],
        [Name("exact_names", Language.get("fr"))],
        100, # different
        False,
        False,
        FontType.TRUETYPE
    )
    assert font_1 != font_7

    font_8 = Font(
        "example",
        0,
        [Name("family_names", Language.get("fr"))],
        [Name("exact_names", Language.get("fr"))],
        400,
        True, # different
        False,
        FontType.TRUETYPE
    )
    assert font_1 != font_8

    font_9 = Font(
        "example",
        0,
        [Name("family_names", Language.get("fr"))],
        [Name("exact_names", Language.get("fr"))],
        400,
        False,
        True,  # different
        FontType.TRUETYPE
    )
    assert font_1 != font_9

    font_10 = Font(
        "example",
        0,
        [Name("family_names", Language.get("fr"))],
        [Name("exact_names", Language.get("fr"))],
        400,
        False,
        False,  
        FontType.OPENTYPE # different
    )
    assert font_1 != font_10


def test__hash__():
    font = Font(
        "exmaple",
        0,
        [Name("family_name", Language.get("en"))],
        [Name("exact_names", Language.get("en"))],
        400,
        False,
        False,
        FontType.TRUETYPE
    )

    assert isinstance(font, Hashable)

    font_1 = Font(
        "example",
        0,
        [Name("family_names", Language.get("fr"))],
        [Name("exact_names", Language.get("fr"))],
        400,
        False,
        False,
        FontType.TRUETYPE
    )

    font_2 = Font(
        "example",
        0,
        [Name("family_names", Language.get("fr"))],
        [Name("exact_names", Language.get("fr"))],
        400,
        False,
        False,
        FontType.TRUETYPE
    )
    assert {font_1} == {font_2}


def test__repr__():
    font_path = "example"
    font_index = 0
    weight = 400
    is_italic = True
    is_glyph_emboldened = False
    font_type = FontType.TRUETYPE

    exact_names = set()

    family_names = [Name("value", Language.get("fr")) ]
    exact_names = [Name("value 1", Language.get("fr")) ]

    font = Font(
        font_path,
        font_index,
        family_names,
        exact_names,
        weight,
        is_italic,
        is_glyph_emboldened,
        font_type
    )

    assert repr(font) == 'Font(Filename="example", Font index="0", Family_names="[Name(value="value", lang_code="fr")]", Exact_names="[Name(value="value 1", lang_code="fr")]", Weight="400", Italic="True", Glyph emboldened="False", Font type="TRUETYPE")'