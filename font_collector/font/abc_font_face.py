from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections.abc import Iterable
from ctypes import byref
from typing import TYPE_CHECKING, Optional

from fontTools.ttLib.ttFont import TTFont
from freetype import (
    FT_Done_Face,
    FT_Done_FreeType,
    FT_Exception,
    FT_Face,
    FT_Get_Char_Index,
    FT_Get_CMap_Format,
    FT_Init_FreeType,
    FT_Library,
    FT_New_Memory_Face,
    FT_Set_Charmap
)
from langcodes import Language, tag_is_valid

from ..exceptions import InvalidLanguageCode, OSNotSupported
from ..system_lang import get_system_lang
from .chinese_variant import ChineseVariant
from .cmap import CMap
from .font_parser import FontParser
from .font_type import FontType
from .name import Name

if TYPE_CHECKING:
    from .font_file import FontFile

__all__ = ["ABCFontFace"]
_logger = logging.getLogger(__name__)


class ABCFontFace(ABC):
    """Represents a font face of a font file.

    Attributes:
        font_index: The index of the font face in the font file.
        family_names: A list of family names associated with the font face.
        exact_names: A list of exact names associated with the font face.
        weight: The weight of the font face. Equivalent of: https://learn.microsoft.com/en-us/typography/opentype/spec/os2#usweightclass
        is_italic: True if the font face is italic, otherwise False.
        is_glyph_emboldened: True if the font face has emboldened glyphs, otherwise False.
        font_type: The type of font face.
        font_file: The font file associated with this font face
    """
    # Make mypy happy
    __font_index: int
    __family_names: list[Name]
    __exact_names: list[Name]
    __weight: int
    __is_italic: bool
    __is_glyph_emboldened: bool
    __font_type: FontType
    __font_file: FontFile | None

    @property
    @abstractmethod
    def font_index(self) -> int:
        pass

    @property
    @abstractmethod
    def family_names(self) -> list[Name]:
        pass

    @property
    @abstractmethod
    def exact_names(self) -> list[Name]:
        pass

    @property
    @abstractmethod
    def weight(self) -> int:
        pass

    @property
    @abstractmethod
    def is_italic(self) -> bool:
        pass

    @property
    @abstractmethod
    def is_glyph_emboldened(self) -> bool:
        pass

    @property
    @abstractmethod
    def font_type(self) -> FontType:
        pass

    @property
    @abstractmethod
    def font_file(self) -> FontFile | None:
        pass

    @abstractmethod
    def link_face_to_a_font_file(self, value: FontFile) -> None:
        # Since there is a circular reference between FontFile and this class, we need to be able to set the value
        pass

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        pass


    @abstractmethod
    def __hash__(self) -> int:
        pass


    @abstractmethod
    def __repr__(self) -> str:
        pass


    def get_family_name_from_lang(self, lang_code: str, exact_match: bool = False) -> Name | None:
        """
        See the doc of _get_name_from_lang
        """
        return self._get_name_from_lang(self.family_names, lang_code, exact_match)


    def get_best_family_name(self) -> Name:
        """
        See the doc of _get_best_name
        """
        return self._get_best_name(self.family_names)


    def get_exact_name_from_lang(self, lang_code: str, exact_match: bool = False) -> Name | None:
        """
        See the doc of _get_name_from_lang
        """
        return self._get_name_from_lang(self.exact_names, lang_code, exact_match)


    def get_best_exact_name(self) -> Name:
        """
        See the doc of _get_best_name
        """
        return self._get_best_name(self.exact_names)


    @staticmethod
    def _get_best_name(names: list[Name]) -> Name:
        """
        Args:
            names: A list of Names. Can be the family_names or exact_names.
        Returns:
            The best names for the user.
            The optimal names for the user are determined based on the following priority order:
                1. Match the system language (ex: "fr") AND system territory (ex: "CA")
                2. Match the system language (ex: "fr")
                3. Match the english language
                4. The first name
            It respects what is written here: https://github.com/libass/libass/wiki/Fonts-across-platforms#createfontindirectselectobject-vsfilter
        """
        ignore_system_lang = False
        try:
            system_lang = get_system_lang()
        except OSNotSupported:
            _logger.warning(f"FontCollector doesn't support your OS. We are not able to get the OS system language.")
            ignore_system_lang = True

        if not ignore_system_lang:
            result = ABCFontFace._get_name_from_lang(names, system_lang, False)
            if result is not None:
                return result

        result = ABCFontFace._get_name_from_lang(names, "en", False)
        if result is not None:
            return result

        return names[0]


    @staticmethod
    def _get_name_from_lang(names: list[Name], lang_code: str, exact_match: bool) -> Name | None:
        """
        Args:
            names: A list of Names. Can be the family_names or exact_names.
            lang_code: An IETF BCP-47 tag (only language, script and territory. Ex: "en", "en-UK", "bs-Latn-BA")
            exact_match:
                - If true, it will return a name with the specified AND script AND territory if it is in the names.
                    Ex: "en-US" can only match with "en-US".
                - If false, it will return a name with the specified language if it is in the names.
                    Ex: "en-US" can match with "en-US", "en", "en-CA", etc...
        Returns:
            The best name that match with the lang_code.
            If none of the names correspond to the lang_code, then it returns None.
            It respects what is written here: https://github.com/libass/libass/wiki/Fonts-across-platforms#createfontindirectselectobject-vsfilter
        """
        if not tag_is_valid(lang_code):
            raise InvalidLanguageCode(f"The language code \"{lang_code}\" does not conform to IETF BCP-47")

        requested_lang = Language.get(lang_code)
        is_requested_chinese = requested_lang.language == "zh"
        if is_requested_chinese:
            requested_chinese_variant = ChineseVariant.from_lang_code(requested_lang)

        MATCH_MAJOR_LANG_OR_SAME_CHINESE_VARIANT = 1
        MATCH_DIFF_CHINESE_VARIANT = 2
        match_level = float('inf')
        best_name: Name | None = None

        for name in names:
            if name.lang_code.language == requested_lang.language:
                is_territory_equal = name.lang_code.territory == requested_lang.territory
                is_script_equal = name.lang_code.script == requested_lang.script

                if is_territory_equal and is_script_equal:
                    best_name = name
                    break

                if not exact_match:
                    if is_requested_chinese:
                        chinese_variant = ChineseVariant.from_lang_code(name.lang_code)
                        is_same_chinese_variant_match = chinese_variant == requested_chinese_variant
                        if is_same_chinese_variant_match:
                            if match_level > MATCH_MAJOR_LANG_OR_SAME_CHINESE_VARIANT:
                                best_name = name
                                match_level = MATCH_MAJOR_LANG_OR_SAME_CHINESE_VARIANT
                        elif match_level > MATCH_DIFF_CHINESE_VARIANT:
                            best_name = name
                            match_level = MATCH_DIFF_CHINESE_VARIANT
                    elif match_level > MATCH_MAJOR_LANG_OR_SAME_CHINESE_VARIANT:
                        best_name = name
                        match_level = MATCH_MAJOR_LANG_OR_SAME_CHINESE_VARIANT

        return best_name


    def get_missing_glyphs(
        self,
        text: Iterable[str],
        support_only_ascii_char_for_symbol_font: bool = False
    ) -> set[str]:
        """
        Args:
            text: An iterable of characters.
            support_only_ascii_char_for_symbol_font (bool):
                Libass only supports ASCII characters for symbol cmap, but VSFilter can support more characters.
                    If you wish to use libass, we recommend you to set this parameter to True.
                    If you wish to use VSFilter, we recommend you to set this parameter to False.
                For more details, see the issue: https://github.com/libass/libass/issues/319
        Returns:
            A set of all the characters that the font doesn't support.
        """
        if self.font_file is None:
            raise ValueError("This font_face isn't linked to any FontFile.")

        char_not_found: set[str] = set()

        library = FT_Library()
        face = FT_Face()

        error = FT_Init_FreeType(byref(library))
        if error: raise FT_Exception(error)

        # We cannot use FT_New_Face due to this issue: https://github.com/rougier/freetype-py/issues/157
        with open(self.font_file.filename, mode="rb") as f:
            filebody = f.read()
        error = FT_New_Memory_Face(library, filebody, len(filebody), self.font_index, byref(face))
        if error: raise FT_Exception(error)

        ttFont = TTFont(self.font_file.filename, fontNumber=self.font_index)
        supported_cmaps = FontParser.get_supported_cmaps(ttFont, self.font_file.filename, self.font_index)
        supported_charmaps = []
        for i in range(face.contents.num_charmaps):
            charmap = face.contents.charmaps[i]
            # Ignore the CMap created by freetype.
            # See: https://freetype.org/freetype2/docs/reference/ft2-truetype_tables.html#ft_get_cmap_format
            if FT_Get_CMap_Format(charmap) == -1:
                continue

            platform_id = charmap.contents.platform_id
            encoding_id = charmap.contents.encoding_id

            cmap = CMap(platform_id, encoding_id)
            if cmap not in supported_cmaps:
                continue

            supported_charmaps.append(charmap)

        for char in text:
            char_found = False

            for charmap in supported_charmaps:
                error = FT_Set_Charmap(face, charmap)
                if error: raise FT_Exception(error)

                platform_id = charmap.contents.platform_id
                encoding_id = charmap.contents.encoding_id

                cmap_encoding = FontParser.get_cmap_encoding(platform_id, encoding_id)

                # cmap not supported
                if cmap_encoding is None:
                    continue

                if cmap_encoding == "unicode":
                    codepoint = ord(char)
                else:
                    symbol_cmap = False
                    if cmap_encoding == "unknown":
                        if platform_id == 3 and encoding_id == 0:
                            symbol_cmap = True
                            if support_only_ascii_char_for_symbol_font and not char.isascii():
                                continue
                            cmap_encoding = FontParser.get_symbol_cmap_encoding(face)

                            if cmap_encoding is None:
                                # Fallback if guess fails
                                cmap_encoding = "cp1252"
                        else:
                            # cmap not supported
                            continue

                    if symbol_cmap and (0xF020 <= ord(char) and ord(char) <= 0xF0FF):
                        # If the character is already a "symbol" character (a.k.a is between 0xF020 and 0xF0FF),
                        # GDI directly use it's codepoint.
                        codepoint = ord(char)
                    else:
                        try:
                            codepoint = int.from_bytes(char.encode(cmap_encoding), "big")
                        except UnicodeEncodeError:
                            continue

                # GDI/Libass modify the codepoint for microsoft symbol cmap.
                # See: https://github.com/libass/libass/blob/04a208d5d200360d2ac75f8f6cfc43dd58dd9225/libass/ass_font.c#L249-L250
                if platform_id == 3 and encoding_id == 0:
                    codepoint = 0xF000 | codepoint

                index = FT_Get_Char_Index(face, codepoint)

                if index:
                    char_found = True
                    break

            if not char_found:
                char_not_found.add(char)

        FT_Done_Face(face)
        FT_Done_FreeType(library)

        return char_not_found
