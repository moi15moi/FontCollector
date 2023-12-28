from __future__ import annotations
from ctypes import byref
from ..ass.ass_style import AssStyle
from ..exceptions import InvalidLanguageCode, OSNotSupported
from ..system_lang import get_system_lang
from .font_parser import FontParser
from .font_type import FontType
from .name import Name, PlatformID
from abc import ABC, abstractmethod
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
    FT_Set_Charmap,
)
from langcodes import Language, tag_is_valid
from typing import List, Sequence, Set, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from .font_file import FontFile



_logger = logging.getLogger(__name__)


class ABCFontFace(ABC):

    @property
    def font_index(self: ABCFontFace) -> int:
        return self._font_index

    @property
    def family_names(self: ABCFontFace) -> List[Name]:
        return self._family_names

    @property
    def exact_names(self: ABCFontFace) -> List[Name]:
        # if the font is a TrueType, it will be the "full_name". if the font is a OpenType, it will be the "postscript name"
        return self._exact_names
    
    @property
    def weight(self: ABCFontFace) -> int:
        return self._weight

    @property
    def is_italic(self: ABCFontFace) -> bool:
        return self._is_italic
    
    @property
    def is_glyph_emboldened(self: ABCFontFace) -> bool:
        return self._is_glyph_emboldened
    
    @property
    def font_type(self: ABCFontFace) -> FontType:
        return self._font_type

    @property
    def font_file(self: ABCFontFace) -> FontFile:
        return self._font_file
    
    def link_face_to_a_font_file(self: ABCFontFace, value: FontFile):
        # Since there is a circular reference between FontFile and this class, we need to be able to set the value
        self._font_file = value

    @abstractmethod
    def __eq__(self: ABCFontFace) -> bool:
        pass


    @abstractmethod
    def __hash__(self: ABCFontFace) -> int:
        pass
    

    @abstractmethod
    def __repr__(self: ABCFontFace) -> str:
        pass


    @abstractmethod
    def get_family_from_lang(self: ABCFontFace) -> List[Name]:
        pass
    

    @abstractmethod
    def get_exact_name_from_lang(self: ABCFontFace) -> List[Name]:
        pass


    def get_family_from_lang(self: ABCFontFace, lang_code: str, exact_match: bool = False) -> List[Name]:
        """
        See the doc of _get_names_from_lang
        """
        return self._get_names_from_lang(self.family_names, lang_code, exact_match)
    

    def get_best_family_from_lang(self: ABCFontFace) -> Name:
        """
        See the doc of _get_best_names_from_lang
        """
        return self._get_best_names_from_lang(self.family_names)


    def get_exact_name_from_lang(self: ABCFontFace, lang_code: str, exact_match: bool = False) -> List[Name]:
        """
        See the doc of _get_names_from_lang
        """
        return self._get_names_from_lang(self.exact_names, lang_code, exact_match)
    

    def get_best_exact_name_from_lang(self: ABCFontFace) -> Name:
        """
        See the doc of _get_best_names_from_lang
        """
        return self._get_best_names_from_lang(self.exact_names)


    @staticmethod
    def _get_lowest_name_lang_code(names: List[Name]) -> Name:
        lowest_lang_code = float('inf')
        selected_name = None
        for name in names:
            try:
                lang_code = name.get_lang_code_platform_code(PlatformID.MICROSOFT)
            except ValueError:
                _logger.warning(f"Could not find the language code of the name {name}. We will ignore the name")
                continue
            if lang_code < lowest_lang_code:
                selected_name = name
        return selected_name


    @staticmethod
    def _get_best_names_from_lang(names: List[Name]) -> Name:
        """
        Parameters:
            names (Set[Name]): A set of Names. Can be the family_names or exact_names.
        Returns:
            A list of the names where the language that is the best for the user.
            Order:
                1. Match the system language (ex: "fr") AND system territory (ex: "CA")
                2. Match the system language (ex: "fr")
                3. Match the english language
                4. Use the first name (sorted by windows language id https://learn.microsoft.com/en-us/typography/opentype/spec/name#windows-language-ids)
        """
        ignore_system_lang = False
        try:
            system_lang = get_system_lang()
        except OSNotSupported:
            _logger.warning(f"FontCollector doesn't support your OS. We are not able to get the OS system language.")
            ignore_system_lang = True

        if not ignore_system_lang:
            results = ABCFontFace._get_names_from_lang(names, system_lang, False)
            if results:
                return results[0]

        results = ABCFontFace._get_names_from_lang(names, "en", False)
        if results:
            return ABCFontFace._get_lowest_name_lang_code(results)
        
        results = ABCFontFace._get_lowest_name_lang_code(names)
        if results:
            return results
        
        # Any value. It can only happen if the font contains only unicode name (platformID=0)
        return next(iter(names))

    
    @staticmethod
    def _get_names_from_lang(names: List[Name], lang_code: str, exact_match: bool) -> List[Name]:
        """
        Parameters:
            names (Set[Name]): A set of Names. Can be the family_names or exact_names.
            lang_code (str): An IETF BCP-47 tag (only language and territory. Ex: "en-UK", "en")
            exact_match (bool):
                - If true, it will return all the names with the specified AND territory. Ex: "en-US" can only match with "en-US".
                - If false, it will return search names with the specified language. Ex: "en-US" can match with "en-US", "en", "en-CA", etc...
        Returns:
            A list of the names that match the specified language.
            If exact_match is False, the returned list will be in an specific order. 
                The Order:
                    1. It prefer the names that match to the requested language and territory (ex: requested: "en-UK" would be "en-UK")
                    2. Then it will prefer the names with only an language (ex: requested: "en-UK" would be "en")
                    3. Then it will prefer the name where an language match but the territory doesn't (ex: "en-UK" if the lang_code="en-CA")

                Ex:
                    names: [Name(value="example_1", lang_code="en-CA"), Name(value="example_2", lang_code="en-UK"), Name(value="example_3", lang_code="en")]
                    lang_code = "en-CA"
                    exact_match = False
                    Return : [Name(value="example_1", lang_code="en-CA"), Name(value="example_3", lang_code="en"), Name(value="example_2", lang_code="en-UK")]
        """
        if not tag_is_valid(lang_code):
            raise InvalidLanguageCode(f"The \"{lang_code}\" does not conform to IETF BCP-47")
        
        parsed_lang = Language.get(lang_code)
        matched_names: List[Name] = []

        for name in names:
            if name.lang_code.language == parsed_lang.language:
                if not exact_match:
                        matched_names.append(name)
                elif name.lang_code.territory == parsed_lang.territory:
                    matched_names.append(name)

        if not exact_match:
            matched_names.sort(key=lambda name: (name.lang_code.territory == parsed_lang.territory, name.lang_code.territory is None), reverse=True)
        return matched_names
    

    def need_faux_bold(self: ABCFontFace, style_weight: int) -> bool:
        return style_weight > self.weight + 150 and not self.is_glyph_emboldened


    def get_similarity_score(self: ABCFontFace, style: AssStyle) -> int:
        """
        Parameters:
            style (AssStyle): An AssStyle
        Returns:
            A matching score - the lower the better. If if it return, it means it is a perfect match.
        """
        score = 0

        if style.italic and not self.is_italic:
            score += 1
        elif not style.italic and self.is_italic:
            score += 4

        weight_compare = self.weight
        if self.need_faux_bold(style.weight):
            weight_compare += 120

        score += (73 * abs(weight_compare - style.weight)) // 256

        if self.font_type not in (FontType.TRUETYPE, FontType.TRUETYPE_COLLECTION):
            score += 9000

        return score


    def get_missing_glyphs(
        self,
        text: Sequence[str],
        support_only_ascii_char_for_symbol_font: bool = False
    ) -> Set[str]:
        """
        Parameters:
            text (Sequence[str]): Text
            support_only_ascii_char_for_symbol_font (bool):
                Libass only support ascii character for symbol cmap, but VSFilter can support more character.
                    If you wish to use libass, we recommand you to set this param to True.
                    If you wish to use VSFilter, we recommand you to set this param to False.
                For more detail, see the issue: https://github.com/libass/libass/issues/319
        Returns:
            A set of all the character that the font cannot display.
        """
        char_not_found: Set[str] = set()

        library = FT_Library()
        face = FT_Face()

        error = FT_Init_FreeType(byref(library))
        if error: raise FT_Exception(error)

        # We cannot use FT_New_Face due to this issue: https://github.com/rougier/freetype-py/issues/157
        with open(self.font_file.filename, mode="rb") as f:
            filebody = f.read()
        error = FT_New_Memory_Face(library, filebody, len(filebody), self.font_index, byref(face))
        if error: raise FT_Exception(error)

        supported_charmaps = [face.contents.charmaps[i] for i in range(face.contents.num_charmaps) if FT_Get_CMap_Format(face.contents.charmaps[i]) != -1 and face.contents.charmaps[i].contents.platform_id == 3]

        # GDI seems to take apple cmap if there isn't any microsoft cmap: https://github.com/libass/libass/issues/679
        if len(supported_charmaps) == 0:
            supported_charmaps = [face.contents.charmaps[i] for i in range(face.contents.num_charmaps) if FT_Get_CMap_Format(face.contents.charmaps[i]) != -1 and face.contents.charmaps[i].contents.platform_id == 1 and face.contents.charmaps[i].contents.encoding_id == 0]

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
                    if cmap_encoding == "unknown":
                        if platform_id == 3 and encoding_id == 0:
                            if support_only_ascii_char_for_symbol_font and not char.isascii():
                                continue
                            cmap_encoding = FontParser.get_symbol_cmap_encoding(face)

                            if cmap_encoding is None:
                                # Fallback if guess fails
                                cmap_encoding = "cp1252"
                        else:
                            # cmap not supported 
                            continue

                    try:
                        codepoint = int.from_bytes(char.encode(cmap_encoding), "big")
                    except UnicodeEncodeError:
                        continue

                # GDI/Libass modify the codepoint for microsoft symbol cmap: https://github.com/libass/libass/blob/04a208d5d200360d2ac75f8f6cfc43dd58dd9225/libass/ass_font.c#L249-L250
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