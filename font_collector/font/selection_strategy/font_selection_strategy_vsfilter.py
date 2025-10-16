from ..abc_font_face import ABCFontFace
from .font_selection_strategy_libass import FontSelectionStrategyLibass

__all__ = ["FontSelectionStrategyVSFilter"]

class FontSelectionStrategyVSFilter(FontSelectionStrategyLibass):
    """
    The FontSelectionStrategyVSFilter is almost the same thing has the FontSelectionStrategyLibass implementation.
    """

    def __trunc_name(self, name: str) -> bytes:
        """
        Truncates a name (family name or exact name) similar to how GDI truncates LOGFONTW::lfFaceName.

        Args:
            name: The input string to be truncated.
        Returns:
            bytes: A truncated byte sequence representing the UTF-16 big-endian encoding of the input string.

        Notes:
            [lfFaceName](https://learn.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-logfontw) contains 32 WCHARs,
            including the null terminator, leaving only 31 WCHARs (Wide Characters) available for the font name.
            WCHARs are encoded as UTF-16-BE and each one occupying 2 bytes: https://learn.microsoft.com/en-us/windows/win32/learnwin32/working-with-strings
            Therefore, the maximum length of the truncated byte sequence is 62 bytes.
            Warning: The size of a character represented in UTF-16 varies from 2 bytes to 4 bytes.
            This method may break a surrogate in two, which is an invalid behavior, but it replicates the behavior of GDI.
        """
        MAX_SIZE = 62
        utf16_bytes = name.encode("utf-16-be")
        max_bytes = min(len(utf16_bytes), MAX_SIZE)

        trunc_utf16_bytes = utf16_bytes[:max_bytes]
        return trunc_utf16_bytes


    def is_font_name_match(self, font_face: ABCFontFace, style_font_name: str) -> bool:
        family_name_match = any(self.__trunc_name(style_font_name.lower()) == self.__trunc_name(family_name.value.lower()) for family_name in font_face.family_names)

        if not family_name_match:
            exact_name_match = any(self.__trunc_name(style_font_name.lower()) == self.__trunc_name(exact_name.value.lower()) for exact_name in font_face.exact_names)

        return family_name_match or exact_name_match
