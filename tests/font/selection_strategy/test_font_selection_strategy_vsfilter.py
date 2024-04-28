from font_collector import Name, NormalFontFace, FontType
from font_collector.font.selection_strategy.font_selection_strategy_vsfilter import FontSelectionStrategyVSFilter
from langcodes import Language


def test_is_font_name_match_trunc_string():
    strategy = FontSelectionStrategyVSFilter()

    family_name_str = "A" * 30 + "\U0001f60b"
    family_name = Name(family_name_str, Language.get("en"))
    font = NormalFontFace(0, [family_name], [family_name], 400, False, False, FontType.TRUETYPE)

    style_font_name = family_name_str
    assert strategy.is_font_name_match(font, style_font_name)

    # Yes, the family_name_str != style_font_name, but it is still a match because
    # \U0001f60c is encoded on 4 bytes, so it will be over the 31 limit characters.
    # Because of the, it is truncated and it only take the first 2 bytes which are
    # the same has \U0001f60b
    style_font_name = "A" * 30 + "\U0001f60c"
    assert strategy.is_font_name_match(font, style_font_name)

    style_font_name = "A" * 30 + "\U0001f752"
    assert strategy.is_font_name_match(font, style_font_name)

    style_font_name = "A" * 30 + "\U0001f852"
    assert not strategy.is_font_name_match(font, style_font_name)


def test_is_font_name_match_family_and_exact_match():
    strategy = FontSelectionStrategyVSFilter()

    family_name = Name("family", Language.get("en"))
    exact_name = Name("exact", Language.get("en"))
    font = NormalFontFace(0, [family_name], [exact_name], 400, False, False, FontType.TRUETYPE)

    assert strategy.is_font_name_match(font, "family")
    assert strategy.is_font_name_match(font, "exact")
    assert not strategy.is_font_name_match(font, "anything")
