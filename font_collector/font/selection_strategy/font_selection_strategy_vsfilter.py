from ...ass.ass_style import AssStyle
from ..abc_font_face import ABCFontFace
from .font_selection_strategy_libass import FontSelectionStrategyLibass
from ..font_type import FontType

__all__ = ["FontSelectionStrategyVSFilter"]

class FontSelectionStrategyVSFilter(FontSelectionStrategyLibass):
    """
    The FontSelectionStrategyVSFilter is almost the same thing has the FontSelectionStrategyLibass implementation.
    """

    def is_font_name_match(self, font_face: ABCFontFace, style_font_name: str) -> bool:
        def trunc_str(string: str) -> bytes:
            utf16_bytes = string.encode("utf-16-be")

            # Calculate maximum number of bytes for truncated string
            # LF_FACESIZE = 32, but it include the null. So, in reality, there is only 31 WCHAR available: https://learn.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-logfontw
            # utf-16-be are 2 or 4 bytes. If 2 bytes, then it use 1 WCHAR, if 4 bytes, then it use 2 WCHAR. So, from what I understand, WCHAR contain 2 bytes.
            # This means lfFaceName can contains 62 bytes.
            max_bytes = min(len(utf16_bytes), 62)

            trunc_utf16_bytes = utf16_bytes[:max_bytes]
            return trunc_utf16_bytes
        
        family_name_match = any(trunc_str(style_font_name.lower()) == trunc_str(family_name.value.lower()) for family_name in font_face.family_names)

        if not family_name_match:
            exact_name_match = any(trunc_str(style_font_name.lower()) == trunc_str(exact_name.value.lower()) for exact_name in font_face.exact_names)
        
        return family_name_match or exact_name_match


    def get_similarity_score(self, font_face: ABCFontFace, style: AssStyle) -> float:
        score = super().get_similarity_score(font_face, style)

        # VSFilter prefer opentype font over truetype font
        # See: https://github.com/libass/libass/issues/437#issuecomment-1925944380
        if font_face.font_type not in (FontType.TRUETYPE, FontType.TRUETYPE_COLLECTION):
            score += 9000

        return score
