import freetype
import logging
from io import BufferedReader
from pathlib import Path
from typing import Dict, List, Set, Tuple, Union
from fontTools.ttLib.ttFont import TTFont
from fontTools.ttLib.tables._n_a_m_e import NameRecord
from fontTools.varLib.instancer import AxisLimits, axisValuesFromAxisLimits
from fontTools.varLib.instancer.names import (
    _isRibbi,
    _sortAxisValues,
    ELIDABLE_AXIS_VALUE_NAME,
    NameID,
)
from struct import error as struct_error

_logger = logging.getLogger(__name__)


class FontParser:
    @staticmethod
    def get_var_font_family_prefix(font: TTFont) -> str:
        """
        From: https://github.com/fonttools/fonttools/blob/3c4cc71504774d1ae4f1e59e3ef3b97e194c1c91/Lib/fontTools/varLib/instancer/names.py#L267-L269

        Parameters:
            font (TTFont): An fontTools object
        Returns:
            The family name prefix.
        """
        family_prefix = FontParser.get_name_by_id(
            NameID.TYPOGRAPHIC_FAMILY_NAME, font["name"].names
        ) or FontParser.get_name_by_id(NameID.FAMILY_NAME, font["name"].names)

        return family_prefix

    @staticmethod
    def get_var_font_family_fullname(
        font: TTFont, axis_value_tables
    ) -> Tuple[str, str]:
        """
        From:
            - https://github.com/fonttools/fonttools/blob/3c4cc71504774d1ae4f1e59e3ef3b97e194c1c91/Lib/fontTools/varLib/instancer/names.py#L195-L232
            - https://github.com/fonttools/fonttools/blob/3c4cc71504774d1ae4f1e59e3ef3b97e194c1c91/Lib/fontTools/varLib/instancer/names.py#L267-L305

        Parameters:
            font (TTFont): An fontTools object
            axis_value_tables: List of axis value
        Returns:
            The family name and the fullname for an axis_value_tables.
        """
        if "STAT" not in font:
            raise ValueError(
                "Cannot get family and fullname since there is no STAT table."
            )

        stat = font["STAT"].table

        axis_value_tables = [
            v for v in axis_value_tables if not v.Flags & ELIDABLE_AXIS_VALUE_NAME
        ]

        axisValueNameIDs = [a.ValueNameID for a in axis_value_tables]
        ribbiNameIDs = [n for n in axisValueNameIDs if _isRibbi(font["name"], n)]
        nonRibbiNameIDs = [n for n in axisValueNameIDs if n not in ribbiNameIDs]
        elidedNameID = stat.ElidedFallbackNameID
        elidedNameIsRibbi = _isRibbi(font["name"], elidedNameID)

        subFamilyName = " ".join(
            FontParser.get_name_by_id(n, font["name"].names) for n in ribbiNameIDs
        )
        if nonRibbiNameIDs:
            typoSubFamilyName = " ".join(
                FontParser.get_name_by_id(n, font["name"].names)
                for n in axisValueNameIDs
            )
        else:
            typoSubFamilyName = None

        # If neither subFamilyName and typographic SubFamilyName exist,
        # we will use the STAT's elidedFallbackName
        if not typoSubFamilyName and not subFamilyName:
            if elidedNameIsRibbi:
                subFamilyName = FontParser.get_name_by_id(
                    elidedNameID, font["name"].names
                )
            else:
                typoSubFamilyName = FontParser.get_name_by_id(
                    elidedNameID, font["name"].names
                )

        familyNameSuffix = " ".join(
            FontParser.get_name_by_id(n, font["name"].names) for n in nonRibbiNameIDs
        )

        currentFamilyName = FontParser.get_var_font_family_prefix(font)

        nameIDs = {
            NameID.FAMILY_NAME: currentFamilyName,
            NameID.SUBFAMILY_NAME: subFamilyName or "Regular",
        }
        if typoSubFamilyName:
            nameIDs[
                NameID.FAMILY_NAME
            ] = f"{currentFamilyName} {familyNameSuffix}".strip()
            nameIDs[NameID.TYPOGRAPHIC_FAMILY_NAME] = currentFamilyName
            nameIDs[NameID.TYPOGRAPHIC_SUBFAMILY_NAME] = typoSubFamilyName

        newFamilyName = (
            nameIDs.get(NameID.TYPOGRAPHIC_FAMILY_NAME) or nameIDs[NameID.FAMILY_NAME]
        )
        newStyleName = (
            nameIDs.get(NameID.TYPOGRAPHIC_SUBFAMILY_NAME)
            or nameIDs[NameID.SUBFAMILY_NAME]
        )

        nameIDs[NameID.FULL_FONT_NAME] = f"{newFamilyName} {newStyleName}"

        return nameIDs[NameID.FAMILY_NAME], nameIDs[NameID.FULL_FONT_NAME]

    @staticmethod
    def get_axis_value_from_coordinates(font: TTFont, coordinates: Dict) -> List:
        """
        Parameters:
            font (TTFont): An fontTools object
            coordinates (Dict): An coordinates from an NamedInstance
        Returns:
            An list of each Axis Value for an coordinates.
        """

        if "STAT" not in font:
            raise ValueError("Cannot get axis_value since there is no STAT table.")
        stat = font["STAT"].table

        # If there isn't any axis, return an empty list
        if stat.AxisValueArray is None:
            return []

        axisLimits = AxisLimits(coordinates).populateDefaults(font)
        axis_value_tables = axisValuesFromAxisLimits(stat, axisLimits)

        return _sortAxisValues(axis_value_tables)

    @staticmethod
    def sort_naming_table(names: List[NameRecord]) -> List[NameRecord]:
        """
        Parameters:
            names (List[NameRecord]): Naming table
        Returns:
            The sorted naming table
        """

        def isEnglish(name: NameRecord) -> bool:
            # From https://gitlab.freedesktop.org/fontconfig/fontconfig/-/blob/d863f6778915f7dd224c98c814247ec292904e30/src/fcfreetype.c#L1111-1125
            return (name.platformID, name.langID) in ((1, 0), (3, 0x409))

        # From	https://gitlab.freedesktop.org/fontconfig/fontconfig/-/blob/d863f6778915f7dd224c98c814247ec292904e30/src/fcfreetype.c#L1078
        # 		https://github.com/freetype/freetype/blob/b98dd169a1823485e35b3007ce707a6712dcd525/include/freetype/ttnameid.h#L86-L91
        PLATFORM_ID_APPLE_UNICODE = 0
        PLATFORM_ID_MACINTOSH = 1
        PLATFORM_ID_ISO = 2
        PLATFORM_ID_MICROSOFT = 3
        PLATFORM_ID_ORDER = [
            PLATFORM_ID_MICROSOFT,
            PLATFORM_ID_APPLE_UNICODE,
            PLATFORM_ID_MACINTOSH,
            PLATFORM_ID_ISO,
        ]

        return sorted(
            names,
            key=lambda name: (
                PLATFORM_ID_ORDER.index(name.platformID),
                name.nameID,
                name.platEncID,
                -isEnglish(name),
                name.langID,
            ),
        )

    @staticmethod
    def get_name_by_id(nameID: int, names: List[NameRecord]) -> str:
        """
        Parameters:
            nameID (int): ID of the name you search
            names (List[NameRecord]): Naming table
        Returns:
            The decoded name
        """

        names = list(filter(lambda name: name.nameID == nameID, names))
        names = FontParser.sort_naming_table(names)

        for name in names:
            try:
                unistr = name.toUnicode()
            except UnicodeDecodeError:
                continue

            return unistr

    @staticmethod
    def get_font_postscript_property(
        font_path: str, font_index: int
    ) -> Union[str, None]:
        """
        Parameters:
            font_path (str): Font path.
            font_index (int): Font index.
        Returns:
            is_italic, weight
        """
        try:
            # Like libass, we use freetype: https://github.com/libass/libass/blob/a2b39cde4ecb74d5e6fccab4a5f7d8ad52b2b1a4/libass/ass_fontselect.c#L326
            postscriptNameByte = freetype.Face(
                Path(font_path).open("rb"), font_index
            ).postscript_name
        except OSError:
            _logger.warning(
                f'Error: Please report this error on github. Attach this font "{font_path}" in your issue and say that the postscript has not been correctly decoded'
            )

        if postscriptNameByte is not None:
            try:
                postscriptName = postscriptNameByte.decode("ASCII")
            except UnicodeDecodeError:
                _logger.warning(
                    f'Error: Please report this error on github. Attach this font "{font_path}" in your issue and say that the postscript has not been correctly decoded'
                )

            if postscriptName is not None:
                return postscriptName

        return None

    @staticmethod
    def get_font_italic_bold_property(
        font: TTFont, font_path: str, font_index: int
    ) -> Tuple[bool, int]:
        """
        Parameters:
            font (TTFont): An fontTools object
            font_path (str): Font path.
            font_index (int): Font index.
        Returns:
            is_italic, weight
        """

        def get_font_italic_bold_property_with_freetype(
            font_path: str, font_index: int
        ) -> Tuple[bool, int]:
            font = freetype.Face(Path(font_path).open("rb"), font_index)
            # From: https://github.com/libass/libass/blob/a2b39cde4ecb74d5e6fccab4a5f7d8ad52b2b1a4/libass/ass_fontselect.c#L318
            is_italic = bool(
                font.style_flags & freetype.ft_enums.ft_style_flags.FT_STYLE_FLAG_ITALIC
            )
            # From: https://github.com/libass/libass/blob/a2b39cde4ecb74d5e6fccab4a5f7d8ad52b2b1a4/libass/ass_font.c#L523
            weight = (
                700
                if bool(
                    font.style_flags
                    & freetype.ft_enums.ft_style_flags.FT_STYLE_FLAG_BOLD
                )
                else 400
            )

            return is_italic, weight

        if "OS/2" in font:
            try:
                # https://docs.microsoft.com/en-us/typography/opentype/spec/os2#fss
                is_italic = bool(font["OS/2"].fsSelection & 1)

                # https://docs.microsoft.com/en-us/typography/opentype/spec/os2#usweightclass
                weight = font["OS/2"].usWeightClass
            except struct_error:
                is_italic, weight = get_font_italic_bold_property_with_freetype(
                    font_path, font_index
                )
        else:
            is_italic, weight = get_font_italic_bold_property_with_freetype(
                font_path, font_index
            )

        # See https://github.com/libass/libass/pull/676
        if weight == 1:
            weight = 100
        elif weight == 2:
            weight = 200
        elif weight == 3:
            weight = 300
        elif weight == 4:
            weight = 350
        elif weight == 5:
            weight = 400
        elif weight == 6:
            weight = 600
        elif weight == 7:
            weight = 700
        elif weight == 8:
            weight = 800
        elif weight == 9:
            weight = 900

        return is_italic, weight

    @staticmethod
    def get_font_family_fullname_property(
        names: List[NameRecord],
    ) -> Tuple[Set[str], Set[str]]:
        """
        Parameters:
            names (List[NameRecord]): Naming table
        Returns:
            All decoded families and fullnames that are from microsoft platform
        """

        # https://github.com/libass/libass/blob/a2b39cde4ecb74d5e6fccab4a5f7d8ad52b2b1a4/libass/ass_fontselect.c#L258-L344
        MAX = 100
        families = set()
        fullnames = set()

        for name in names:

            if name.platformID == 3 and (name.nameID == 1 or name.nameID == 4):

                try:
                    # Since we use the windows platform, we can simply use utf_16_be to decode the string: https://docs.microsoft.com/en-us/typography/opentype/spec/name#platform-specific-encoding-and-language-ids-windows-platform-platform-id-3
                    # Even libass always use utf_16_be: https://github.com/libass/libass/blob/a2b39cde4ecb74d5e6fccab4a5f7d8ad52b2b1a4/libass/ass_fontselect.c#L283
                    nameStr = name.string.decode("utf_16_be")
                except UnicodeDecodeError:
                    continue

                if name.nameID == 1 and len(families) < MAX:
                    families.add(nameStr)
                elif name.nameID == 4 and len(fullnames) < MAX:
                    fullnames.add(nameStr)

        return families, fullnames

    @staticmethod
    def is_file_truetype_collection(file: BufferedReader) -> bool:
        file.seek(0)
        return b"ttcf" == file.read(4)

    @staticmethod
    def is_file_truetype(file: BufferedReader) -> bool:
        file.seek(0)
        return b"\x00\x01\x00\x00\x00" == file.read(5)

    @staticmethod
    def is_file_opentype(file: BufferedReader) -> bool:
        file.seek(0)
        return b"OTTO" == file.read(4)

    @staticmethod
    def is_file_font(filepath: str) -> bool:
        with open(filepath, "rb") as fontFile:
            return (
                FontParser.is_file_truetype(fontFile)
                or FontParser.is_file_opentype(fontFile)
                or FontParser.is_file_truetype_collection(fontFile)
            )
