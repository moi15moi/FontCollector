from __future__ import annotations
from ..exceptions import InvalidNameRecord
from .lcid import WINDOWS_LANGUAGES_TO_LCID_CODE, WINDOWS_LCID_CODE_TO_LANGUAGES
from enum import IntEnum
from fontTools.ttLib.tables._n_a_m_e import _MAC_LANGUAGES, _MAC_LANGUAGE_CODES, NameRecord
from langcodes import closest_supported_match, Language
from typing import Dict, Optional, Type

MAC_LCID_CODE_TO_LANGUAGES: dict[int, str] = _MAC_LANGUAGES
MAC_LANGUAGES_TO_LCID_CODE: dict[str, int] = _MAC_LANGUAGE_CODES


__all__ = ["Name", "NameID", "PlatformID"]

class PlatformID(IntEnum):
    # From https://learn.microsoft.com/en-us/typography/opentype/spec/name#platform-ids
    UNICODE = 0
    MACINTOSH = 1
    MICROSOFT = 3


class NameID(IntEnum):
    # From: https://learn.microsoft.com/en-us/typography/opentype/spec/name#name-ids
    COPYRIGHT = 0
    FAMILY_NAME = 1
    SUBFAMILY_NAME = 2
    UNIQUE_ID = 3
    FULL_NAME = 4
    VERSION_STRING = 5
    POSTSCRIPT_NAME = 6
    TRADEMARK = 7
    MANUFACTURER = 8
    DESIGNER = 9
    DESCRIPTION = 10
    VENDOR_URL = 11
    DESIGNER_URL = 12
    LICENSE_DESCRIPTION = 13
    LICENSE_URL = 14
    TYPOGRAPHIC_FAMILY_NAME = 16
    TYPOGRAPHIC_SUBFAMILY_NAME = 17
    MAC_FULL_NAME = 18
    SAMPLE_TEXT = 19
    POSTSCRIPT_CID_FINDFONT_NAME = 20
    WWS_FAMILY_NAME = 21
    WWS_SUBFAMILY_NAME = 22
    LIGHT_BACKGROUND = 23
    DARK_BACKGROUND = 24
    VARIATIONS_PREFIX_NAME = 25


class Name:
    """Represents a font name with associated language information.

    Attributes:
        value: The actual name value. Ex: "Arial"
        lang_code: The language code associated with the name.
            In some very specific case, the lang_code can be "und" (undefined)
    """

    def __init__(
        self,
        value: str,
        lang_code: Language
    ) -> None:
        self.value = value
        self.lang_code = lang_code


    @classmethod
    def from_name_record(cls: type[Name], name_record: NameRecord) -> Name:
        """
        Args:
            name_record: Name record from the naming table
        Returns:
            An Name instance.
        """
        value = Name.get_decoded_name_record(name_record)
        lang_code = Language.get(Name.get_lang_code_of_namerecord(name_record))

        return cls(value, lang_code)


    @staticmethod
    def get_name_record_encoding(name: NameRecord) -> Optional[str]:
        """
        Args:
            names: Name record from the naming table
        Returns:
            The NameRecord encoding name.
            If GDI does not support the NameRecord, it return None.
        """
        # From: https://github.com/MicrosoftDocs/typography-issues/issues/956#issuecomment-1205678068
        if name.platformID == PlatformID.MICROSOFT:
            if name.platEncID == 3:
                return "cp936"
            elif name.platEncID == 4:
                if name.nameID == NameID.SUBFAMILY_NAME:
                    return "utf_16_be"
                else:
                    return "cp950"
            elif name.platEncID == 5:
                if name.nameID == NameID.SUBFAMILY_NAME:
                    return "utf_16_be"
                else:
                    return "cp949"
            else:
                return "utf_16_be"
        elif name.platformID == PlatformID.MACINTOSH and name.platEncID == 0:
            # From: https://github.com/libass/libass/issues/679#issuecomment-1442262479
            return "iso-8859-1"

        return None


    @staticmethod
    def get_decoded_name_record(name: NameRecord) -> str:
        """
        Args:
            names: Name record from the naming table
        Returns:
            The decoded name
        """
        encoding = Name.get_name_record_encoding(name)

        if encoding is None:
            raise InvalidNameRecord(f"The NameRecord you provided isn't supported by GDI: NameRecord(PlatformID={name.platformID}, PlatEncID={name.platEncID}, LangID={name.langID}, String={name.string}, NameID={name.nameID})")

        name_to_decode: bytes
        if name.platformID == PlatformID.MICROSOFT and encoding != "utf_16_be":
            # I spoke with a Microsoft employee and he told me that GDI performed this processing:
            name_to_decode = name.string.replace(b"\x00", b"")
        else:
            name_to_decode = name.string

        # GDI ignore any decoding error. See tests\font tests\Test #1\Test #1.py
        return name_to_decode.decode(encoding, "ignore")


    @staticmethod
    def get_lang_code_of_namerecord(name: NameRecord) -> str:
        """
        Args:
            names: Name record from the naming table
        Returns:
            The IETF BCP-47 code of the NameRecord. If the lang code isn't found, it return "und".
        """
        return Name.get_bcp47_lang_code_from_name_record(name.platformID, name.langID if hasattr(name, "langID") else -1)


    @staticmethod
    def get_bcp47_lang_code_from_name_record(platform_id: PlatformID, lang_id: int = -1) -> str:
        """
        Args:
            platform_id: An platform id.
            lang_id: An language id of an platform. See: https://learn.microsoft.com/en-us/typography/opentype/spec/name
                For the unicode platform, you don't need to give the lang_id
        Returns:
            The IETF BCP-47 code corresponding to the language id. If the lang code isn't found, it return "und".
        """
        if platform_id == PlatformID.MICROSOFT:
            return WINDOWS_LCID_CODE_TO_LANGUAGES.get(lang_id, "und")
        elif platform_id == PlatformID.MACINTOSH:
            return MAC_LCID_CODE_TO_LANGUAGES.get(lang_id, "und")
        else:
            return "und"


    def get_lang_id_from_platform_id(self, platform_id: PlatformID, fallback_to_language: bool = False) -> int:
        """
        Args:
            platform_id: The platform id of which you wanna retrieve the lang_code
            fallback_to_language: If the platform doesn't support the language, try to only match the a language with a different regional (ex: en-US with en-GB)
        Returns:
            The language code corresponding to the platform:
                - https://learn.microsoft.com/en-us/typography/opentype/spec/name#macintosh-language-ids
                - https://learn.microsoft.com/en-us/typography/opentype/spec/name#windows-language-ids
        """
        tag_distance = 9 if fallback_to_language else 0
        if platform_id == PlatformID.MICROSOFT:
            result = closest_supported_match(self.lang_code, list(WINDOWS_LANGUAGES_TO_LCID_CODE.keys()), tag_distance)
            if result is None:
                raise ValueError(f'The lang_code "{self.lang_code.to_tag()}" isn\'t supported by the microsoft platform')
            return WINDOWS_LANGUAGES_TO_LCID_CODE[result]
        elif platform_id == PlatformID.MACINTOSH:
            result = closest_supported_match(self.lang_code, list(MAC_LANGUAGES_TO_LCID_CODE.keys()), tag_distance)
            if result is None:
                raise ValueError(f'The lang_code "{self.lang_code.to_tag()}" isn\'t supported by the macintosh platform')
            return MAC_LANGUAGES_TO_LCID_CODE[result]
        raise ValueError(f"You cannot specify the platform id {platform_id}. You can only specify the microsoft or the macintosh id")


    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Name):
            return False
        return (self.value, self.lang_code) == (other.value, other.lang_code)


    def __hash__(self) -> int:
        return hash((self.value, self.lang_code))


    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(value="{self.value}", lang_code="{self.lang_code}")'
