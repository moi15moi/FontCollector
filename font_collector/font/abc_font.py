from __future__ import annotations
from ..ass.ass_style import AssStyle
from ..exceptions import InvalidLanguageCode, OSNotSupported
from ..system_lang import get_system_lang
from .font_parser import FontParser
from .font_type import FontType
from .name import Name, PlatformID
from abc import ABC, abstractmethod
from fontTools.ttLib.ttFont import TTFont
from langcodes import Language, tag_is_valid
from typing import List, Sequence, Set
import logging


_logger = logging.getLogger(__name__)


class ABCFont(ABC):

    @property
    def filename(self: ABCFont) -> str:
        return self.__filename

    @filename.setter
    def filename(self: ABCFont, value: str):
        self.__filename = value


    @property
    def font_index(self: ABCFont) -> int:
        return self.__font_index

    @font_index.setter
    def font_index(self: ABCFont, value: int):
        self.__font_index = value


    @property
    def family_names(self: ABCFont) -> Set[Name]:
        return self.__family_names

    @family_names.setter
    def family_names(self: ABCFont, value: Set[Name]):
        self.__family_names = value


    @property
    def exact_names(self: ABCFont) -> Set[Name]:
        # if the font is a TrueType, it will be the "full_name". if the font is a OpenType, it will be the "postscript name"
        return self.__exact_names
    
    @exact_names.setter
    def exact_names(self: ABCFont, value: Set[Name]):
        self.__exact_names = value


    @property
    def weight(self: ABCFont) -> int:
        return self.__weight

    @weight.setter
    def weight(self: ABCFont, value: int):
        self.__weight = value


    @property
    def is_italic(self: ABCFont) -> bool:
        return self.__is_italic
    
    @is_italic.setter
    def is_italic(self: ABCFont, value: bool):
        self.__is_italic = value


    @property
    def is_glyph_emboldened(self: ABCFont) -> bool:
        return self.__is_glyph_emboldened
    
    @is_glyph_emboldened.setter
    def is_glyph_emboldened(self: ABCFont, value: bool):
        self.__is_glyph_emboldened = value


    @property
    def font_type(self: ABCFont) -> FontType:
        return self.__font_type

    @font_type.setter
    def font_type(self: ABCFont, value: FontType):
        self.__font_type = value


    @abstractmethod
    def __eq__(self: ABCFont) -> bool:
        pass


    @abstractmethod
    def __hash__(self: ABCFont) -> int:
        pass
    

    @abstractmethod
    def __repr__(self: ABCFont) -> str:
        pass


    @abstractmethod
    def get_family_from_lang(self: ABCFont) -> List[Name]:
        pass
    

    @abstractmethod
    def get_exact_name_from_lang(self: ABCFont) -> List[Name]:
        pass


    def get_family_from_lang(self: ABCFont, lang_code: str, exact_match: bool = False) -> List[Name]:
        """
        See the doc of _get_names_from_lang
        """
        return self._get_names_from_lang(self.family_names, lang_code, exact_match)
    

    def get_best_family_from_lang(self: ABCFont) -> Name:
        """
        See the doc of _get_best_names_from_lang
        """
        return self._get_best_names_from_lang(self.family_names)


    def get_exact_name_from_lang(self: ABCFont, lang_code: str, exact_match: bool = False) -> List[Name]:
        """
        See the doc of _get_names_from_lang
        """
        return self._get_names_from_lang(self.exact_names, lang_code, exact_match)
    

    def get_best_exact_name_from_lang(self: ABCFont) -> Name:
        """
        See the doc of _get_best_names_from_lang
        """
        return self._get_best_names_from_lang(self.exact_names)


    @staticmethod
    def _get_lowest_name_lang_code(names: Set[Name]) -> Name:
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
    def _get_best_names_from_lang(names: Set[Name]) -> Name:
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
            results = ABCFont._get_names_from_lang(names, system_lang, False)
            if results:
                return results[0]

        results = ABCFont._get_names_from_lang(names, "en", False)
        if results:
            return ABCFont._get_lowest_name_lang_code(results)
        
        results = ABCFont._get_lowest_name_lang_code(names)
        if results:
            return results
        
        # Any value. It can only happen if the font contains only unicode name (platformID=0)
        return next(iter(names))

    
    @staticmethod
    def _get_names_from_lang(names: Set[Name], lang_code: str, exact_match: bool) -> List[Name]:
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


    def get_similarity_score(self: ABCFont, style: AssStyle) -> int:
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
        if style.weight > self.weight + 150 and not self.is_glyph_emboldened:
            weight_compare += 120

        score += (73 * abs(weight_compare - style.weight)) // 256

        if self.font_type != FontType.TRUETYPE:
            score += 9000

        return score


    def get_missing_glyphs(self: ABCFont, text: Sequence[str]) -> Set[str]:
        """
        Parameters:
            text (Sequence[str]): Text
        Returns:
            A set of all the character that the font cannot display.
        """

        ttFont = TTFont(self.filename, fontNumber=self.font_index)
        char_not_found: Set[str] = set()

        cmap_tables = FontParser.get_supported_cmaps(ttFont["cmap"].tables)

        for char in text:
            char_found = False

            for cmap_table in cmap_tables:
                cmap_encoding = FontParser.get_cmap_encoding(cmap_table)

                # Cmap isn't supported
                if cmap_encoding is None:
                    continue

                try:
                    codepoint = int.from_bytes(char.encode(cmap_encoding), "big")
                except UnicodeEncodeError:
                    continue

                # GDI/Libass modify the codepoint for microsoft symbol cmap: https://github.com/libass/libass/blob/04a208d5d200360d2ac75f8f6cfc43dd58dd9225/libass/ass_font.c#L249-L250
                if cmap_table.platformID == PlatformID.MICROSOFT and cmap_table.platEncID == 0:
                    codepoint = 0xF000 | codepoint

                if codepoint in cmap_table.cmap:
                    char_found = True
                    break

            if not char_found:
                char_not_found.add(char)

        return char_not_found