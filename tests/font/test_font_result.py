import os
from font_collector import FontResult, FontType, Name, NormalFontFace
from langcodes import Language
from typing import Hashable

dir_path = os.path.dirname(os.path.realpath(__file__))


def test__init__():
    font = NormalFontFace(
        0,
        [Name("family_names", Language.get("en"))],
        [Name("exact_names", Language.get("en"))],
        400,
        False,
        False,
        FontType.TRUETYPE
    )
    mismatch_bold = True
    need_faux_bold = True
    mismatch_italic = False

    font_result = FontResult(font, mismatch_bold, need_faux_bold, mismatch_italic)

    assert font_result.font_face == font
    assert font_result.mismatch_bold == mismatch_bold
    assert font_result.need_faux_bold == need_faux_bold
    assert font_result.mismatch_italic == mismatch_italic


def test__eq__():
    font_face_1 = NormalFontFace(
        0,
        [Name("family_names", Language.get("fr"))],
        [Name("exact_names", Language.get("fr"))],
        400,
        False,
        False,
        FontType.TRUETYPE
    )
    font_face_2 = NormalFontFace(
        0,
        [Name("family_names diff", Language.get("fr"))],
        [Name("exact_names", Language.get("fr"))],
        400,
        False,
        False,
        FontType.TRUETYPE
    )

    font_result_1 = FontResult(font_face_1, True, True, True)
    font_result_2 = FontResult(font_face_1, True, True, True)
    assert font_result_1 == font_result_2

    font_result_3 = FontResult(font_face_2, True, True, True)
    assert font_result_1 != font_result_3

    font_result_4 = FontResult(font_face_1, False, True, True)
    assert font_result_1 != font_result_4

    font_result_5 = FontResult(font_face_1, True, False, True)
    assert font_result_1 != font_result_5

    font_result_6 = FontResult(font_face_1, True, True, False)
    assert font_result_1 != font_result_6

    assert font_result_1 != "test"

def test__hash__():
    font_face_1 = NormalFontFace(
        0,
        [Name("family_names", Language.get("fr"))],
        [Name("exact_names", Language.get("fr"))],
        400,
        False,
        False,
        FontType.TRUETYPE
    )
    font_face_2 = NormalFontFace(
        0,
        [Name("family_names diff", Language.get("fr"))],
        [Name("exact_names", Language.get("fr"))],
        400,
        False,
        False,
        FontType.TRUETYPE
    )

    font_result_1 = FontResult(font_face_1, True, True, True)
    font_result_2 = FontResult(font_face_1, True, True, True)
    assert isinstance(font_result_1, Hashable)
    assert {font_result_1} == {font_result_2}

    font_result_3 = FontResult(font_face_2, True, True, True)
    assert {font_result_1} != {font_result_3}

    font_result_4 = FontResult(font_face_1, False, True, True)
    assert {font_result_1} != font_result_4

    font_result_5 = FontResult(font_face_1, True, False, True)
    assert {font_result_1} != {font_result_5}

    font_result_6 = FontResult(font_face_1, True, True, False)
    assert {font_result_1} != {font_result_6}

    assert {font_result_1} != {"test"}

def test__repr__():
    font = NormalFontFace(
        0,
        [Name("family_names", Language.get("en"))],
        [Name("exact_names", Language.get("en"))],
        400,
        False,
        False,
        FontType.TRUETYPE
    )
    mismatch_bold = True
    need_faux_bold = True
    mismatch_italic = False

    font_result = FontResult(font, mismatch_bold, need_faux_bold, mismatch_italic)
    assert repr(font_result) == 'FontResult(Font face="NormalFontFace(Font index="0", Family names="[Name(value="family_names", lang_code="en")]", Exact names="[Name(value="exact_names", lang_code="en")]", Weight="400", Italic="False", Glyph emboldened="False", Font type="TRUETYPE")", Mismatch bold="True", Need faux bold="True", Mismatch italic="False")'
