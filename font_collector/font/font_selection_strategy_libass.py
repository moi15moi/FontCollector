from ..ass.ass_style import AssStyle
from .abc_font_face import ABCFontFace
from .font_selection_strategy import FontSelectionStrategy
from .font_type import FontType

__all__ = ["FontSelectionStrategyLibass"]

class FontSelectionStrategyLibass(FontSelectionStrategy):
    """
    FontSelectionStrategyLibass is an implementation of the FontSelectionStrategy interface
    that utilizes a modified version of the algorithm described in the following sources:

    - Original algorithm: https://github.com/libass/libass/pull/678
    - Windows shared algorithm (1992): https://msdn.microsoft.com/en-us/library/ms969909.aspx#actual-weights

    This implementation includes additional handling for truetype vs opentype fonts, inspired
    by the behavior observed in VSFilter.

    Note: The Windows shared algorithm from 1992 may have been modified since then.
    """


    def need_faux_bold(self, font_face: ABCFontFace, style: AssStyle) -> bool:
        return style.weight > font_face.weight + 150 and not font_face.is_glyph_emboldened


    def get_similarity_score(self, font_face: ABCFontFace, style: AssStyle) -> float:
        score = 0.0

        family_name_match = any(style.fontname.lower() == family_name.value.lower() for family_name in font_face.family_names)

        if not family_name_match:
            exact_name_match = any(style.fontname.lower() == exact_name.value.lower() for exact_name in font_face.exact_names)
            if not exact_name_match:
                return float("inf")

        if style.italic and not font_face.is_italic:
            score += 1
        elif not style.italic and font_face.is_italic:
            score += 4

        weight_compare = font_face.weight
        if self.need_faux_bold(font_face, style):
            weight_compare += 120

        score += (73 * abs(weight_compare - style.weight)) // 256

        if font_face.font_type not in (FontType.TRUETYPE, FontType.TRUETYPE_COLLECTION):
            score += 9000
        
        from .variable_font_face import VariableFontFace
        if isinstance(font_face, VariableFontFace):
            score += 0.5

        return score
