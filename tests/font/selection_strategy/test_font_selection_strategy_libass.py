from langcodes import Language

from font_collector import FontType, Name, NormalFontFace
from font_collector.font.selection_strategy.font_selection_strategy_libass import (
    FontSelectionStrategyLibass
)


def test_is_font_name_match_trunc_string():
    strategy = FontSelectionStrategyLibass()

    family_name_str = "A" * 30 + "\U0001f60b"
    family_name = Name(family_name_str, Language.get("en"))
    font = NormalFontFace(0, [family_name], [family_name], 400, False, False, FontType.TRUETYPE)

    style_font_name = family_name_str
    assert strategy.is_font_name_match(font, style_font_name)

    style_font_name = "A" * 30 + "\U0001f60c"
    assert not strategy.is_font_name_match(font, style_font_name)

    style_font_name = "A" * 30 + "\U0001f752"
    assert not strategy.is_font_name_match(font, style_font_name)

    style_font_name = "A" * 30 + "\U0001f852"
    assert not strategy.is_font_name_match(font, style_font_name)


def test_is_font_name_match_family_and_exact_match():
    strategy = FontSelectionStrategyLibass()

    family_name = Name("family", Language.get("en"))
    exact_name = Name("exact", Language.get("en"))
    font = NormalFontFace(0, [family_name], [exact_name], 400, False, False, FontType.TRUETYPE)

    assert strategy.is_font_name_match(font, "family")
    assert strategy.is_font_name_match(font, "exact")
    assert not strategy.is_font_name_match(font, "anything")
