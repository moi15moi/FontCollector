from ...ass.ass_style import AssStyle
from ..abc_font_face import ABCFontFace
from .font_selection_strategy import FontSelectionStrategy


__all__ = ["FontSelectionStrategyLibass"]

class FontSelectionStrategyLibass(FontSelectionStrategy):
    """
    FontSelectionStrategyLibass is an implementation of the FontSelectionStrategy interface
    that utilizes a modified version of the algorithm described in the following sources:

    - Original algorithm: https://github.com/libass/libass/pull/678
    - Windows shared algorithm (1992): https://msdn.microsoft.com/en-us/library/ms969909.aspx#actual-weights

    Note: The Windows shared algorithm from 1992 may have been modified since then.
    """

    def is_font_name_match(self, font_face: ABCFontFace, style_font_name: str) -> bool:
        family_name_match = any(style_font_name.casefold() == family_name.value.casefold() for family_name in font_face.family_names)

        if not family_name_match:
            exact_name_match = any(style_font_name.casefold() == exact_name.value.casefold() for exact_name in font_face.exact_names)

        return family_name_match or exact_name_match


    def need_faux_bold(self, font_face: ABCFontFace, style: AssStyle) -> bool:
        return style.weight > font_face.weight + 150 and not font_face.is_glyph_emboldened


    def get_similarity_score(self, font_face: ABCFontFace, style: AssStyle) -> float:
        score = 0.0

        if not self.is_font_name_match(font_face, style.fontname):
            return float("inf")

        if style.italic and not font_face.is_italic:
            score += 1
        elif not style.italic and font_face.is_italic:
            score += 4

        weight_compare = font_face.weight
        if self.need_faux_bold(font_face, style):
            weight_compare += 120

        score += (73 * abs(weight_compare - style.weight)) // 256

        # This is NOT part of the actual GDI algorith, BUT if we don't prefer Normal font over variable font,
        # when a user call VariableFontFace.variable_font_to_collection, the created font will have the same score has
        # the variable font AND since the variable font is older than the font collection, it will prefer the variable font
        # which is not what we want.
        from ..variable_font_face import VariableFontFace
        if isinstance(font_face, VariableFontFace):
            score += 0.5

        return score
