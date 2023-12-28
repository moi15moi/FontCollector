import collections
import os
import pytest
import string
from font_collector import FontFile, FontType, InvalidLanguageCode, Name, NormalFontFace
from langcodes import Language
from typing import Hashable

dir_path = os.path.dirname(os.path.realpath(__file__))


def test__init__():
    font_index = 0
    family_names = [Name("family_names", Language.get("en"))]
    exact_names = [Name("exact_names", Language.get("en"))]
    weight = 400
    is_italic = False
    is_glyph_emboldened = False
    font_type = FontType.TRUETYPE

    font = NormalFontFace(
        font_index,
        family_names,
        exact_names,
        weight,
        is_italic,
        is_glyph_emboldened,
        font_type
    )

    assert font.font_index == font_index
    assert font.family_names == family_names
    assert font.exact_names == exact_names
    assert font.weight == weight
    assert font.is_italic == is_italic
    assert font.is_glyph_emboldened == is_glyph_emboldened
    assert font.font_type == font_type
    assert font.font_file == None


def test_font_index_property():
    font = NormalFontFace(0, [Name("test", Language.get("en"))], [], 400, False, False, FontType.TRUETYPE)
    font_index = 1
    with pytest.raises(AttributeError) as exc_info:
        font.font_index = font_index
    assert str(exc_info.value) == "property 'font_index' of 'NormalFontFace' object has no setter"


def test_family_names_property():
    font = NormalFontFace(0, [Name("test", Language.get("en"))], [], 400, False, False, FontType.TRUETYPE)
    family_names = [Name("test", Language.get("en"))]
    with pytest.raises(AttributeError) as exc_info:
        font.family_names = family_names
    assert str(exc_info.value) == "property 'family_names' of 'NormalFontFace' object has no setter"


def test_exact_names_property():
    font = NormalFontFace(0, [Name("test", Language.get("en"))], [], 400, False, False, FontType.TRUETYPE)
    exact_names = [Name("test", Language.get("en"))]
    with pytest.raises(AttributeError) as exc_info:
        font.exact_names = exact_names
    assert str(exc_info.value) == "property 'exact_names' of 'NormalFontFace' object has no setter"


def test_weight_property():
    font = NormalFontFace(0, [Name("test", Language.get("en"))], [], 400, False, False, FontType.TRUETYPE)
    weight = 900
    with pytest.raises(AttributeError) as exc_info:
        font.weight = weight
    assert str(exc_info.value) == "property 'weight' of 'NormalFontFace' object has no setter"


def test_is_italic_property():
    font = NormalFontFace(0, [Name("test", Language.get("en"))], [], 400, False, False, FontType.TRUETYPE)
    is_italic = True
    with pytest.raises(AttributeError) as exc_info:
        font.is_italic = is_italic
    assert str(exc_info.value) == "property 'is_italic' of 'NormalFontFace' object has no setter"


def test_is_glyph_emboldened_property():
    font = NormalFontFace(0, [Name("test", Language.get("en"))], [], 400, False, False, FontType.TRUETYPE)
    is_glyph_emboldened = True
    with pytest.raises(AttributeError) as exc_info:
        font.is_glyph_emboldened = is_glyph_emboldened
    assert str(exc_info.value) == "property 'is_glyph_emboldened' of 'NormalFontFace' object has no setter"


def test_font_type():
    font = NormalFontFace(0, [Name("test", Language.get("en"))], [], 400, False, False, FontType.TRUETYPE)
    font_type = FontType.OPENTYPE
    with pytest.raises(AttributeError) as exc_info:
        font.font_type = font_type
    assert str(exc_info.value) == "property 'font_type' of 'NormalFontFace' object has no setter"


def test_link_face_to_a_font_file():
    font = NormalFontFace(0, [Name("test", Language.get("en"))], [], 400, False, False, FontType.TRUETYPE)
    font_file = FontFile("", set())
    font.link_face_to_a_font_file(font_file)
    assert font.font_file == font_file


def test_font_get_missing_glyphs_cmap_encoding_0():
    font_cmap_encoding_0 = os.path.join(os.path.dirname(dir_path), "fonts", "font_cmap_encoding_0.TTF")
    font_file = FontFile.from_font_path(font_cmap_encoding_0)

    assert len(font_file.font_faces) == 1
    font_face = font_file.font_faces[0]
    assert isinstance(font_face, NormalFontFace)

    # Verify is the optional param is the right value
    missing_glyphs = font_face.get_missing_glyphs("Έκθεση για Απασχόληση Dream Top Co. Οι επιλογές À a")
    assert missing_glyphs == set("À")

    missing_glyphs = font_face.get_missing_glyphs("Έκθεση για Απασχόληση Dream Top Co. Οι επιλογές À a", False)
    assert missing_glyphs == set("À")

    missing_glyphs = font_face.get_missing_glyphs("Έκθεση για Απασχόληση Dream Top Co. Οι επιλογές À a", True)
    assert missing_glyphs == set("ΈκθεσηγιαπασχόλησηΟιεπιλογέςÀΑ")


def test_font_get_missing_glyphs_cmap_encoding_1():
    font_cmap_encoding_1 = os.path.join(os.path.dirname(dir_path), "fonts", "font_cmap_encoding_1.TTF")
    font_file = FontFile.from_font_path(font_cmap_encoding_1)

    assert len(font_file.font_faces) == 1
    font_face = font_file.font_faces[0]
    assert isinstance(font_face, NormalFontFace)

    missing_glyphs = font_face.get_missing_glyphs(string.digits + "🇦🤍")
    assert missing_glyphs == set()


def test_font_get_missing_glyphs_cmap_encoding_2():
    font_cmap_encoding_2 = os.path.join(os.path.dirname(dir_path), "fonts", "font_cmap_encoding_2.TTF")
    font_file = FontFile.from_font_path(font_cmap_encoding_2)

    assert len(font_file.font_faces) == 1
    font_face = font_file.font_faces[0]
    assert isinstance(font_face, NormalFontFace)

    # Try "é" since cp932 doesn't support this char
    missing_glyphs = font_face.get_missing_glyphs(
        string.ascii_letters + string.digits + "éｦ&*"
    )
    assert missing_glyphs == {"é"}


def test_font_get_missing_glyphs_cmap_encoding_mac_platform():
    font_mac_platform = os.path.join(os.path.dirname(dir_path), "fonts", "font_mac.TTF")
    font_file = FontFile.from_font_path(font_mac_platform)

    assert len(font_file.font_faces) == 1
    font_face = font_file.font_faces[0]
    assert isinstance(font_face, NormalFontFace)

    missing_glyphs = font_face.get_missing_glyphs(string.ascii_letters + string.digits + "@é¸^Æ~")
    assert missing_glyphs == {"@", "¸", "~"}


def test_get_family_and_exact_from_lang():
    font_index = 0
    weight = 400
    italic = True
    is_glyph_emboldened = False
    font_type = FontType.TRUETYPE

    name_1 = Name("", Language.get("fr")) 
    name_2 = Name("", Language.get("fr-CA")) 
    name_3 = Name("", Language.get("fr-BE")) 

    family_names = [name_1, name_2, name_3]
    exact_names = []

    font = NormalFontFace(
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
    exact_names = family_names
    family_names = [Name("anything", Language.get("es"))]
    font = NormalFontFace(
        font_index,
        family_names,
        exact_names,
        weight,
        italic,
        is_glyph_emboldened,
        font_type
    )

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
    font_1 = NormalFontFace(
        0,
        [Name("family_names", Language.get("fr"))],
        [Name("exact_names", Language.get("fr"))],
        400,
        False,
        False,
        FontType.TRUETYPE
    )
    assert font_1 == font_1

    font_2 = NormalFontFace(
        0,
        [Name("family_names", Language.get("fr"))],
        [Name("exact_names", Language.get("fr"))],
        400,
        False,
        False,
        FontType.TRUETYPE
    )
    assert font_1 == font_2

    font_4 = NormalFontFace(
        1, # different
        [Name("family_names", Language.get("fr"))],
        [Name("exact_names", Language.get("fr"))],
        400,
        False,
        False,
        FontType.TRUETYPE
    )
    assert font_1 != font_4

    font_5 = NormalFontFace(
        0,
        [Name("family_names different", Language.get("fr"))], # different
        [Name("exact_names", Language.get("fr"))],
        400,
        False,
        False,
        FontType.TRUETYPE
    )
    assert font_1 != font_5

    font_6 = NormalFontFace(
        0,
        [Name("family_names", Language.get("fr"))],
        [Name("exact_names different", Language.get("fr"))], # different
        400,
        False,
        False,
        FontType.TRUETYPE
    )
    assert font_1 != font_6

    font_7 = NormalFontFace(
        0,
        [Name("family_names", Language.get("fr"))],
        [Name("exact_names", Language.get("fr"))],
        100, # different
        False,
        False,
        FontType.TRUETYPE
    )
    assert font_1 != font_7

    font_8 = NormalFontFace(
        0,
        [Name("family_names", Language.get("fr"))],
        [Name("exact_names", Language.get("fr"))],
        400,
        True, # different
        False,
        FontType.TRUETYPE
    )
    assert font_1 != font_8

    font_9 = NormalFontFace(
        0,
        [Name("family_names", Language.get("fr"))],
        [Name("exact_names", Language.get("fr"))],
        400,
        False,
        True,  # different
        FontType.TRUETYPE
    )
    assert font_1 != font_9

    font_10 = NormalFontFace(
        0,
        [Name("family_names", Language.get("fr"))],
        [Name("exact_names", Language.get("fr"))],
        400,
        False,
        False,  
        FontType.OPENTYPE # different
    )
    assert font_1 != font_10

    font_11 = NormalFontFace(
        0,
        [Name("family_names_1", Language.get("fr")), Name("family_names_2", Language.get("fr"))],
        [Name("exact_names", Language.get("fr"))],
        400,
        False,
        False,  
        FontType.TRUETYPE,
    )
    font_12 = NormalFontFace(
        0,
        [Name("family_names_2", Language.get("fr")), Name("family_names_1", Language.get("fr"))], # order different
        [Name("exact_names", Language.get("fr"))],
        400,
        False,
        False,  
        FontType.TRUETYPE,
    )
    assert font_11 != font_12

    font_13 = NormalFontFace(
        0,
        [Name("family_names", Language.get("fr"))],
        [Name("exact_names_1", Language.get("fr")), Name("exact_names_2", Language.get("fr"))],
        400,
        False,
        False,  
        FontType.TRUETYPE,
    )
    font_14 = NormalFontFace(
        0,
        [Name("family_names", Language.get("fr"))],
        [Name("exact_names_2", Language.get("fr")), Name("exact_names_1", Language.get("fr"))], # order different
        400,
        False,
        False,  
        FontType.TRUETYPE,
    )
    assert font_13 != font_14

def test__hash__():
    font = NormalFontFace(
        0,
        [Name("family_name", Language.get("en"))],
        [Name("exact_names", Language.get("en"))],
        400,
        False,
        False,
        FontType.TRUETYPE
    )

    assert isinstance(font, Hashable)

    font_1 = NormalFontFace(
        0,
        [Name("family_names_1", Language.get("fr")), Name("family_names_2", Language.get("fr"))],
        [Name("exact_names", Language.get("fr"))],
        400,
        False,
        False,
        FontType.TRUETYPE,
    )

    font_2 = NormalFontFace(
        0,
        [Name("family_names_2", Language.get("fr")), Name("family_names_1", Language.get("fr"))],
        [Name("exact_names", Language.get("fr"))],
        400,
        False,
        False,
        FontType.TRUETYPE,
    )
    assert {font_1} != {font_2}

    font_3 = NormalFontFace(
        0,
        [Name("family_names_1", Language.get("fr")), Name("family_names_2", Language.get("fr"))],
        [Name("exact_names", Language.get("fr"))],
        400,
        False,
        False,
        FontType.TRUETYPE,
    )
    assert {font_1} == {font_3}



def test__repr__():
    font_index = 0
    weight = 400
    is_italic = True
    is_glyph_emboldened = False
    font_type = FontType.TRUETYPE

    exact_names = set()

    family_names = [Name("value", Language.get("fr"))]
    exact_names = [Name("value 1", Language.get("fr"))]

    font = NormalFontFace(
        font_index,
        family_names,
        exact_names,
        weight,
        is_italic,
        is_glyph_emboldened,
        font_type
    )

    assert repr(font) == 'NormalFontFace(Font index="0", Family names="[Name(value="value", lang_code="fr")]", Exact names="[Name(value="value 1", lang_code="fr")]", Weight="400", Italic="True", Glyph emboldened="False", Font type="TRUETYPE")'
