import freetype
import logging
from .exceptions import NameNotFoundException
from enum import IntEnum
from io import BufferedReader
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from fontTools.ttLib.ttFont import TTFont
from fontTools.ttLib.tables._n_a_m_e import NameRecord
from fontTools.varLib.instancer.names import ELIDABLE_AXIS_VALUE_NAME
from struct import error as struct_error

_logger = logging.getLogger(__name__)


class NameID(IntEnum):
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


class FontParser:
    DEFAULT_WEIGHT = 400
    DEFAULT_ITALIC = False

    CMAP_ENCODING_MAP = {
        1: {  # Mac
            0: "mac_roman",
        },
        3: {  # Microsoft
            0: "unicode",
            1: "unicode",
            2: "cp932",
            3: "cp936",
            4: "cp950",
            5: "cp949",
            6: "cp1361",
            10: "unicode",
        },
    }

    @staticmethod
    def is_truetype(font: TTFont) -> bool:
        """
        Parameters:
            font (TTFont): An fontTools object
        Returns:
            An boolean that indicate if the font is an Truetype font or not.
            If not, then, it is an Opentype font.
        """
        return "glyf" in font

    @staticmethod
    def is_valid_variable_font(font: TTFont) -> bool:
        """
        Parameters:
            font (TTFont): An fontTools object
        Returns:
            An boolean that indicate if the font is an variable font or not.
        """

        if "fvar" not in font or "STAT" not in font:
            return False

        if font["STAT"].table is None:
            return False

        for axe in font["fvar"].axes:
            if not (axe.minValue <= axe.defaultValue <= axe.maxValue):
                return False

        if font["STAT"].table.AxisValueArray is not None:
            for axis_value in font["STAT"].table.AxisValueArray.AxisValue:
                if axis_value.Format in (1, 2, 3, 4):
                    if axis_value.Format == 4 and len(axis_value.AxisValueRecord) == 0:
                        return False
                else:
                    return False

        return True

    @staticmethod
    def get_var_font_family_prefix(font: TTFont) -> str:
        """
        From: https://github.com/fonttools/fonttools/blob/3c4cc71504774d1ae4f1e59e3ef3b97e194c1c91/Lib/fontTools/varLib/instancer/names.py#L267-L269

        Parameters:
            font (TTFont): An fontTools object
        Returns:
            The family name prefix.
        """
        try:
            family_prefix = FontParser.get_name_by_id(
                NameID.TYPOGRAPHIC_FAMILY_NAME, font["name"].names
            )
        except NameNotFoundException:
            family_prefix = FontParser.get_name_by_id(
                NameID.FAMILY_NAME, font["name"].names
            )

        return family_prefix

    @staticmethod
    def get_distance_between_axis_value_and_coordinates(
        font: TTFont, coordinates: Dict[str, float], axis_value: Any, axis_format: int
    ) -> float:
        """
        Parameters:
            ttfont (TTFont): An fontTools object
            coordinates (Dict[str, float]): The coordinates of an NamedInstance in the fvar table.
            axis_value (Any): An AxisValue
            axis_format (int): The AxisValue Format.
                Since the AxisValue from AxisValueRecord of an AxisValue Format 4 doesn't contain an Format attribute, this parameter is needed.
        Returns:
            The distance between_axis_value_and_coordinates
        """

        axis_tag = (
            font["STAT"].table.DesignAxisRecord.Axis[axis_value.AxisIndex].AxisTag
        )
        instance_value = coordinates.get(axis_tag, 0)

        if axis_format == 2:
            clamped_axis_value = max(
                min(instance_value, axis_value.RangeMaxValue),
                axis_value.RangeMinValue,
            )
        else:
            clamped_axis_value = axis_value.Value

        delta = clamped_axis_value - instance_value
        delta_square = delta**2

        if delta < 0:
            adjust = 1
        else:
            adjust = 0

        distance = delta_square * 2 + adjust

        return distance

    @staticmethod
    def get_axis_value_from_coordinates(
        ttfont: TTFont, coordinates: Dict[str, float]
    ) -> List[Any]:
        """
        Parameters:
            ttfont (TTFont): An fontTools object
            coordinates (Dict[str, float]): The coordinates of an NamedInstance in the fvar table.
        Returns:
            An list who contain all the AxisValue linked to the coordinates.
        """

        distances_for_axis_values: List[Tuple[float, Any]] = []

        if ttfont["STAT"].table.AxisValueArray is None:
            return distances_for_axis_values

        for axis_value in ttfont["STAT"].table.AxisValueArray.AxisValue:

            if axis_value.Format == 4:
                distance = 0

                for axis_value_format_4 in axis_value.AxisValueRecord:
                    distance += (
                        FontParser.get_distance_between_axis_value_and_coordinates(
                            ttfont, coordinates, axis_value_format_4, axis_value.Format
                        )
                    )

                distances_for_axis_values.append((distance, axis_value))

            else:
                distance = FontParser.get_distance_between_axis_value_and_coordinates(
                    ttfont, coordinates, axis_value, axis_value.Format
                )
                distances_for_axis_values.append((distance, axis_value))

        # Sort by ASC
        distances_for_axis_values.sort(key=lambda distance: distance[0])

        axis_values_coordinate_matches: List[Any] = []
        is_axis_useds: List[bool] = [False] * len(
            ttfont["STAT"].table.DesignAxisRecord.Axis
        )

        for distance, axis_value in distances_for_axis_values:
            if axis_value.Format == 4:

                # The AxisValueRecord can have "internal" duplicate axis, but it cannot have duplicate Axis with the other AxisValue
                is_any_duplicate_axis = False
                for axis_value_format_4 in axis_value.AxisValueRecord:
                    if is_axis_useds[axis_value_format_4.AxisIndex]:
                        is_any_duplicate_axis = True
                        break

                if not is_any_duplicate_axis:
                    for axis_value_format_4 in axis_value.AxisValueRecord:
                        is_axis_useds[axis_value_format_4.AxisIndex] = True

                    axis_values_coordinate_matches.append(axis_value)
            else:
                if not is_axis_useds[axis_value.AxisIndex]:
                    is_axis_useds[axis_value.AxisIndex] = True
                    axis_values_coordinate_matches.append(axis_value)

        return axis_values_coordinate_matches

    @staticmethod
    def get_axis_value_table_property(
        ttfont: TTFont, axis_values: List[Any], family_name_prefix: str
    ) -> Tuple[str, str, float, bool]:
        """
        Parameters:
            ttfont (TTFont): An fontTools object
            axis_values (List[Any]): An list of AxisValue.
            family_name_prefix (str): The variable family name prefix.
                Ex: For the name "Alegreya Italic", "Alegreya" is the family name prefix.
        Returns:
            An FontFace that represent the axis_values.
        """

        axis_values.sort(
            key=lambda axis_value: ttfont["STAT"]
            .table.DesignAxisRecord.Axis[
                min(
                    axis_value.AxisValueRecord,
                    key=lambda axis_value_format_4: ttfont["STAT"]
                    .table.DesignAxisRecord.Axis[axis_value_format_4.AxisIndex]
                    .AxisOrdering,
                ).AxisIndex
            ]
            .AxisOrdering
            if axis_value.Format == 4
            else ttfont["STAT"]
            .table.DesignAxisRecord.Axis[axis_value.AxisIndex]
            .AxisOrdering
        )

        family_axis_value = []
        fullname_axis_value = []
        weight = FontParser.DEFAULT_WEIGHT
        italic = FontParser.DEFAULT_ITALIC

        for axis_value in axis_values:

            # If the Format 4 only contain only 1 AxisValueRecord, it will treat it as an single AxisValue like the Format 1, 2 or 3.
            if axis_value.Format == 4 and len(axis_value.AxisValueRecord) > 1:
                if not axis_value.Flags & ELIDABLE_AXIS_VALUE_NAME:
                    family_axis_value.append(axis_value)
                    fullname_axis_value.append(axis_value)
            else:
                if axis_value.Format == 2:
                    value = axis_value.NominalValue
                    axis_index = axis_value.AxisIndex
                elif axis_value.Format in (1, 3):
                    value = axis_value.Value
                    axis_index = axis_value.AxisIndex
                elif axis_value.Format == 4:
                    value = axis_value.AxisValueRecord[0].Value
                    axis_index = axis_value.AxisValueRecord[0].AxisIndex

                if (
                    ttfont["STAT"].table.DesignAxisRecord.Axis[axis_index].AxisTag
                    == "wght"
                ):
                    weight = value
                elif (
                    ttfont["STAT"].table.DesignAxisRecord.Axis[axis_index].AxisTag
                    == "ital"
                ):
                    italic = value == 1

                if not (axis_value.Flags & ELIDABLE_AXIS_VALUE_NAME):
                    fullname_axis_value.append(axis_value)

                    use_in_family_name = True
                    if (
                        ttfont["STAT"].table.DesignAxisRecord.Axis[axis_index].AxisTag
                        == "wght"
                    ):
                        use_in_family_name = value not in (400, 700)
                    elif (
                        ttfont["STAT"].table.DesignAxisRecord.Axis[axis_index].AxisTag
                        == "ital"
                    ):
                        use_in_family_name = value not in (0, 1)

                    if use_in_family_name:
                        family_axis_value.append(axis_value)

        try:
            family_name = f'{family_name_prefix} {" ".join(FontParser.get_name_by_id(axis_value.ValueNameID, ttfont["name"].names) for axis_value in family_axis_value)}'.strip(
                " "
            )
        except NameNotFoundException:
            family_name = family_name_prefix

        if len(fullname_axis_value) == 0:
            try:
                full_name = f"{family_name_prefix} {FontParser.get_name_by_id(ttfont['STAT'].table.ElidedFallbackNameID, ttfont['name'].names)}".strip(
                    " "
                )
            except NameNotFoundException:
                weight = FontParser.DEFAULT_WEIGHT
                italic = FontParser.DEFAULT_ITALIC
                full_name = f"{family_name_prefix} Regular"

        else:
            try:
                full_name = f'{family_name_prefix} {" ".join(FontParser.get_name_by_id(axis_value.ValueNameID, ttfont["name"].names) for axis_value in fullname_axis_value)}'.strip(
                    " "
                )
            except NameNotFoundException:
                weight = FontParser.DEFAULT_WEIGHT
                italic = FontParser.DEFAULT_ITALIC

                try:
                    full_name = f"{family_name_prefix} {FontParser.get_name_by_id(ttfont['STAT'].table.ElidedFallbackNameID, ttfont['name'].names)}".strip(
                        " "
                    )
                except NameNotFoundException:
                    full_name = f"{family_name_prefix} Regular"

        return family_name, full_name, weight, italic

    @staticmethod
    def sort_naming_table(names: List[NameRecord]) -> List[NameRecord]:
        """
        Parameters:
            names (List[NameRecord]): Naming table
        Returns:
            The sorted naming table
        """

        def is_english(name: NameRecord) -> bool:
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
                -is_english(name),
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
                name_str = FontParser.get_decoded_name(name)
            except UnicodeDecodeError:
                continue

            return name_str

        raise NameNotFoundException(
            f"The NamingTable doesn't contain the NameID {nameID}"
        )

    @staticmethod
    def get_decoded_name(name: NameRecord) -> str:
        """
        Parameters:
            names (NameRecord): Name record from the naming record
        Returns:
            The decoded name
        """

        encoding = FontParser.get_name_encoding(name)

        if name.platformID == 3 and encoding != "utf_16_be":
            # I spoke with a Microsoft employee and he told me that GDI performed this processing:
            name_to_decode = name.string.replace(b"\x00", b"")
        else:
            name_to_decode = name.string

        return name_to_decode.decode(encoding)

    @staticmethod
    def get_font_postscript_property(font_path: str, font_index: int) -> Optional[str]:
        """
        Parameters:
            font_path (str): Font path.
            font_index (int): Font index.
        Returns:
            The postscript name
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

            if name.platformID == 3 and (
                name.nameID == NameID.FAMILY_NAME or name.nameID == NameID.FULL_NAME
            ):

                try:
                    name_str = FontParser.get_decoded_name(name)
                except UnicodeDecodeError:
                    continue

                if name.nameID == 1 and len(families) < MAX:
                    families.add(name_str)
                elif name.nameID == 4 and len(fullnames) < MAX:
                    fullnames.add(name_str)

        return families, fullnames

    @staticmethod
    def get_cmap_encoding(platform_id: int, encoding_id: int) -> Optional[str]:
        """
        Parameters:
            platform_id (int): CMAP platform id
            encoding_id (int): CMAP encoding id
        Returns:
            The cmap codepoint encoding.
            If GDI does not support the platform_id and/or platform_encoding_id, return None.
        """
        return FontParser.CMAP_ENCODING_MAP.get(platform_id, {}).get(encoding_id, None)

    @staticmethod
    def get_name_encoding(name: NameRecord) -> Optional[str]:
        """
        Parameters:
            names (NameRecord): Name record from the naming record
        Returns:
            The cmap codepoint encoding.
            If GDI does not support the name, return None.
        """
        # From: https://github.com/MicrosoftDocs/typography-issues/issues/956#issuecomment-1205678068
        if name.platformID == 3:
            if name.platEncID == 3:
                return "cp936"
            elif name.platEncID == 4:
                if name.nameID == 2:
                    return "utf_16_be"
                else:
                    return "cp950"
            elif name.platEncID == 5:
                if name.nameID == 2:
                    return "utf_16_be"
                else:
                    return "cp949"
            else:
                return "utf_16_be"
        elif name.platformID == 1 and name.platEncID == 0:
            # From: https://github.com/libass/libass/issues/679#issuecomment-1442262479
            return "iso-8859-1"

        return None

    @staticmethod
    def is_file_truetype_collection(file: BufferedReader) -> bool:
        file.seek(0)
        return b"ttcf" == file.read(4)

    @staticmethod
    def is_file_truetype(file: BufferedReader) -> bool:
        file.seek(0)
        return b"\x00\x01\x00\x00" == file.read(4)

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
