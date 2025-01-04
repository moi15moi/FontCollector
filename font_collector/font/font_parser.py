from __future__ import annotations
from ..exceptions import InvalidNameRecord, InvalidVariableFontFaceException
from .cmap import CMap
from .name import Name, NameID, PlatformID
from ctypes import byref, c_uint, create_string_buffer
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
from fontTools.ttLib.tables._n_a_m_e import NameRecord
from fontTools.ttLib.ttFont import TTFont
from fontTools.varLib.instancer.names import ELIDABLE_AXIS_VALUE_NAME
from freetype import (
    Face,
    FT_Face,
    FT_Get_Glyph_Name,
)
from freetype.ft_enums.ft_style_flags import FT_STYLE_FLAGS
from itertools import product
from langcodes import Language
from pathlib import Path
from struct import error as struct_error
from typing import Any, Optional


class FontParser:
    """
    A utility class providing static methods for proper font parsing.
    """

    DEFAULT_WEIGHT = 400
    DEFAULT_ITALIC = False
    CMAP_ENCODING_MAP: dict[PlatformID, dict[int, str]] = {
        PlatformID.MACINTOSH: {
            0: "mac_roman",
        },
        PlatformID.MICROSOFT: {
            0: "unknown",
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
    def is_valid_variable_font(font: TTFont) -> bool:
        """
        Args:
            font: The font to be validated
        Returns:
            An boolean that indicate if the font is an variable font or not.
        """

        if "fvar" not in font or "STAT" not in font:
            return False

        if font["STAT"].table is None:
            return False

        if font["STAT"].table.DesignAxisRecord is None:
            raise InvalidVariableFontFaceException("The font has a stat table, but it doesn't have any DesignAxisRecord")

        if not font["fvar"].instances:
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
    def get_var_font_family_prefix(names: list[NameRecord], platform_id: PlatformID) -> list[Name]:
        """Extracts variable font family prefix names based on the provided NameRecord list and platform ID.

        Args:
            names: A list of NameRecord objects.
            platform_id: The platform ID specifying the target platform for family name extraction.
        Returns:
            A list of Name objects representing variable font family prefix names.
        """
        family_prefix = FontParser.get_filtered_names(names, platformID=platform_id, nameID=NameID.TYPOGRAPHIC_FAMILY_NAME)

        if not family_prefix:
            family_prefix = FontParser.get_filtered_names(names, platformID=platform_id, nameID=NameID.FAMILY_NAME)

        return family_prefix

    @staticmethod
    def get_distance_between_axis_value_and_coordinates(
        font: TTFont, coordinates: dict[str, float], axis_value: Any, axis_format: int
    ) -> float:
        """Calculate the distance between an axis value and coordinates of a NamedInstance in a variable font.

        This method is inspired by how GDI parses Variable Fonts. Ensure to call FontParser.is_valid_variable_font()
        before using this method.

        Args:
            font: A fontTools object representing the font.
            coordinates: The coordinates of a NamedInstance in the fvar table.
            axis_value: An AxisValue object representing the font axis value.
                Even if the type is Any, it isn't. It is AxisValueRecord, but fontTools create this class dynamically.
            axis_format (int): The AxisValue format.
        Returns:
            The calculated distance between the specified axis value and coordinates.
        """
        try:
            axis_tag = font["STAT"].table.DesignAxisRecord.Axis[axis_value.AxisIndex].AxisTag
        except IndexError:
            raise InvalidVariableFontFaceException(f"The DesignAxisRecord doesn't contain an axis at the index {axis_value.AxisIndex}")

        # If the coordinates cannot be found, default to 0
        instance_value = coordinates.get(axis_tag, 0)

        clamped_axis_value: float
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
    def get_axis_value_from_coordinates(font: TTFont, coordinates: dict[str, float]) -> list[Any]:
        """Retrieve AxisValue objects linked to the specified coordinates in the fvar table.
        Ensure to call FontParser.is_valid_variable_font() before using this method.

        Args:
            font: A fontTools object representing the font.
            coordinates: The coordinates of a NamedInstance in the fvar table.
        Returns:
            A list containing all the AxisValue objects that has the closest distance
            to the provided coordinates.
        """
        distances_for_axis_values: list[tuple[float, Any]] = []

        if font["STAT"].table.AxisValueArray is None:
            return distances_for_axis_values

        for axis_value in font["STAT"].table.AxisValueArray.AxisValue:

            if axis_value.Format == 4:
                distance = 0.0

                for axis_value_format_4 in axis_value.AxisValueRecord:
                    distance += (
                        FontParser.get_distance_between_axis_value_and_coordinates(
                            font, coordinates, axis_value_format_4, axis_value.Format
                        )
                    )

                distances_for_axis_values.append((distance, axis_value))

            else:
                distance = FontParser.get_distance_between_axis_value_and_coordinates(
                    font, coordinates, axis_value, axis_value.Format
                )
                distances_for_axis_values.append((distance, axis_value))

        # Sort by ASC
        distances_for_axis_values.sort(key=lambda distance: distance[0])

        axis_values_coordinate_matches: list[Any] = []
        is_axis_useds: list[bool] = [False] * len(font["STAT"].table.DesignAxisRecord.Axis)

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
        font: TTFont, axis_values: list[Any]
    ) -> tuple[list[Name], list[Name], float, bool]:
        """Retrieve font properties such as family name, full name, weight, and italic based on axis values.
        Ensure to call FontParser.is_valid_variable_font() before using this method.

        Args:
            font: A fontTools object representing the font.
            axis_values: A list of AxisValue object representing the font axis value.
        Returns:
            A tuple containing the family name, the full name, the weight, and italic.
        """
        axis_values.sort(
            key=lambda axis_value: font["STAT"]
            .table.DesignAxisRecord.Axis[
                min(
                    axis_value.AxisValueRecord,
                    key=lambda axis_value_format_4: font["STAT"]
                    .table.DesignAxisRecord.Axis[axis_value_format_4.AxisIndex]
                    .AxisOrdering,
                ).AxisIndex
            ]
            .AxisOrdering
            if axis_value.Format == 4
            else font["STAT"]
            .table.DesignAxisRecord.Axis[axis_value.AxisIndex]
            .AxisOrdering
        )

        weight = FontParser.DEFAULT_WEIGHT
        italic = FontParser.DEFAULT_ITALIC

        axis_values_names: list[list[Name]] = []
        family_name_axis_value_index: list[bool] = [False] * len(axis_values)
        fullname_axis_value_index: list[bool] = [False] * len(axis_values)


        for i, axis_value in enumerate(axis_values):

            axis_value_name = FontParser.get_filtered_names(font["name"].names, platformID=PlatformID.MICROSOFT, nameID=axis_value.ValueNameID)
            if not axis_value_name:
                raise InvalidVariableFontFaceException("An axis value has an invalid ValueNameID")
            axis_values_names.append(axis_value_name)

            # If the Format 4 only contain only 1 AxisValueRecord, it will treat it as an single AxisValue like the Format 1, 2 or 3.
            if axis_value.Format == 4 and len(axis_value.AxisValueRecord) > 1:
                if not (axis_value.Flags & ELIDABLE_AXIS_VALUE_NAME):
                    family_name_axis_value_index[i] = True
                    fullname_axis_value_index[i] = True
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

                if font["STAT"].table.DesignAxisRecord.Axis[axis_index].AxisTag == "wght":
                    weight = value
                elif font["STAT"].table.DesignAxisRecord.Axis[axis_index].AxisTag == "ital":
                    italic = value == 1

                if not (axis_value.Flags & ELIDABLE_AXIS_VALUE_NAME):
                    fullname_axis_value_index[i] = True

                    use_in_family_name = True
                    if font["STAT"].table.DesignAxisRecord.Axis[axis_index].AxisTag == "wght":
                        use_in_family_name = value not in (400, 700)
                    elif font["STAT"].table.DesignAxisRecord.Axis[axis_index].AxisTag == "ital":
                        use_in_family_name = value not in (0, 1)

                    if use_in_family_name:
                        family_name_axis_value_index[i] = True

        family_name: list[Name] = []
        fullname: list[Name] = []

        # Generate family_name an fullname
        for item in product(*axis_values_names):
            langs: list[Language] = []
            for element in item:
                langs.append(element.lang_code)

            family_name_str = " ".join([element.value for i, element in enumerate(item) if family_name_axis_value_index[i]])
            fullname_str = " ".join([element.value for i, element in enumerate(item) if fullname_axis_value_index[i]])

            family_name.extend([Name(family_name_str, lang) for lang in langs])
            fullname.extend([Name(fullname_str, lang) for lang in langs])

        if all(not element for element in fullname_axis_value_index):
            # Fallback if all the element have the flag ELIDABLE_AXIS_VALUE_NAME
            if hasattr(font['STAT'].table, "ElidedFallbackNameID"):
                elided_fallback_name = FontParser.get_filtered_names(font['name'].names, platformID=PlatformID.MICROSOFT, nameID=font['STAT'].table.ElidedFallbackNameID)

                if elided_fallback_name:
                    fullname = elided_fallback_name
                else:
                    # The elided_fallback_name haven't been found
                    weight = FontParser.DEFAULT_WEIGHT
                    italic = FontParser.DEFAULT_ITALIC
                    fullname = [Name(f"Regular", Language.get("en-US"))]
            else:
                fullname = [Name(f"Normal", Language.get("en-US"))]

        # Remove duplicate name while preserving the order
        family_name = list(dict.fromkeys(family_name))
        fullname = list(dict.fromkeys(fullname))

        return family_name, fullname, weight, italic


    @staticmethod
    def get_filtered_names(
        names_record: list[NameRecord],
        platformID: Optional[PlatformID] = None,
        platEncID: Optional[int] = None,
        nameID: Optional[NameID] = None,
        langID: Optional[int] = None,
        skip_unsupported_name_record: bool = True
    ) -> list[Name]:
        """Retrieve and decode NameRecord objects based on specified filtering criteria.
        Is it the same criteria has: https://learn.microsoft.com/en-us/typography/opentype/spec/name#name-records

        Args:
            names_record: A list of NameRecord objects representing the naming table.
            platformID: Filter the names_record by platformID.
            platEncID: Filter the names_record by platEncID.
            nameID: Filter the names_record by nameID.
            langID: Filter the names_record by langID.
            skip_unsupported_name_record: When trying to decode NameRecord, the exception InvalidNameRecord can be raised.
                If this argument is true, then it will ignore the exception and discard the NameRecord.
        Returns:
            A list of the decoded NameRecord objects that have been filtered.
        """
        names: list[Name] = []

        for name_record in names_record:
            if (
                (platformID is None or name_record.platformID == platformID) and
                (platEncID is None or name_record.platEncID == platEncID) and
                (nameID is None or name_record.nameID == nameID) and
                (langID is None or name_record.langID == langID)
            ):
                try:
                    names.append(Name.from_name_record(name_record))
                except InvalidNameRecord:
                    if not skip_unsupported_name_record:
                        raise

        return names


    @staticmethod
    def get_font_italic_bold_property_with_freetype(
        font_path: Path, font_index: int
    ) -> tuple[bool, bool, int]:
        """
        Args:
            font_path: Font path.
            font_index: Font index.
        Returns:
            is_italic, is_glyphs_emboldened, weight
        """
        with font_path.open("rb") as f:
            face = Face(f, font_index)
        is_italic = bool(face.style_flags & FT_STYLE_FLAGS["FT_STYLE_FLAG_ITALIC"])
        is_glyphs_emboldened = bool(face.style_flags & FT_STYLE_FLAGS["FT_STYLE_FLAG_BOLD"])
        weight = 700 if is_glyphs_emboldened else 400

        return is_italic, is_glyphs_emboldened, weight


    @staticmethod
    def get_font_italic_bold_property_microsoft_platform(
        font: TTFont, font_path: Path, font_index: int
    ) -> tuple[bool, bool, int]:
        """
        Args:
            font: An fontTools object
            font_path: Font path.
            font_index: Font index.
        Returns:
            is_italic, is_glyphs_emboldened, weight
        """

        if "OS/2" in font:
            try:
                # https://docs.microsoft.com/en-us/typography/opentype/spec/os2#fss
                is_italic = bool(font["OS/2"].fsSelection & 1)
                is_glyphs_emboldened = bool(font["OS/2"].fsSelection & 1 << 5)
                # https://docs.microsoft.com/en-us/typography/opentype/spec/os2#usweightclass
                weight = font["OS/2"].usWeightClass
            except struct_error:
                is_italic, is_glyphs_emboldened, weight = FontParser.get_font_italic_bold_property_with_freetype(font_path, font_index)
        else:
            is_italic, is_glyphs_emboldened, weight = FontParser.get_font_italic_bold_property_with_freetype(font_path, font_index)

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

        return is_italic, is_glyphs_emboldened, weight


    @staticmethod
    def get_font_italic_bold_property_mac_platform(
        font: TTFont, font_path: Path, font_index: int
    ) -> tuple[bool, bool, int]:
        """
        Args:
            font: An fontTools object
            font_path: Font path.
            font_index: Font index.
        Returns:
            is_italic, is_glyphs_emboldened, weight
        """
        if "head" in font:
            try:
                # https://learn.microsoft.com/en-us/typography/opentype/spec/head
                # https://github.com/libass/libass/issues/679#issuecomment-1404520010
                is_italic = bool(font["head"].macStyle & 1 << 1)
                is_glyphs_emboldened = bool(font["head"].macStyle & 1)
                weight = 800 if is_glyphs_emboldened else 400
            except struct_error:
                is_italic, is_glyphs_emboldened, weight = FontParser.get_font_italic_bold_property_with_freetype(font_path, font_index)
        else:
            is_italic, is_glyphs_emboldened, weight = FontParser.get_font_italic_bold_property_with_freetype(font_path, font_index)

        return is_italic, is_glyphs_emboldened, weight


    @staticmethod
    def get_symbol_cmap_encoding(face: FT_Face) -> Optional[str]:
        """
        Args:
            face: An Font face
        Returns:
            The cmap ansi code page encoding.
            If it couldn't guess the encoding, it return None.
                It can return none if the font doesn't use any unique character of an ansi code page.
                    Note: Chinese (cp936 or cp950) and Korean (cp949) doesn't contain any unique character.
                          So, we can't recognized them.
            Libass currently has an issue about this problem: https://github.com/libass/libass/issues/319
            When Libass will add the logic with the track language, this method will be deprecated.
        """
        font_glyph_names: set[str] = set()
        # This is a limit set by adobe: http://adobe-type-tools.github.io/afdko/OpenTypeFeatureFileSpecification.html#2fi-glyph-name
        buffer_max = 64
        for i in range(face.contents.num_glyphs):
            buffer = create_string_buffer(buffer_max)
            error = FT_Get_Glyph_Name(face, c_uint(i), byref(buffer), c_uint(buffer_max))

            if error:
                continue
            font_glyph_names.add(buffer.value.decode("ascii").casefold())

        count_codepage: dict[str, int] = {}
        for code_page, glyph_names in UNIQUE_ADOBE_GLYPH_NAME_BY_CODE_PAGE.items():
            count = sum(1 for font_glyph_name in font_glyph_names if font_glyph_name in glyph_names)
            count_codepage[code_page] = count

        if len(count_codepage) == 0:
            return None
        # If there is a tie, prefer codepage different then cp1252
        codepage_encoding = max(count_codepage, key=lambda codepage: (count_codepage[codepage], codepage != 'cp1252'))

        return codepage_encoding


    @staticmethod
    def get_supported_cmaps(
        font: TTFont, font_path: Path, font_index: int
    ) -> list[CMap]:
        """
        Retrieve supported CMaps from a TrueType font.

        Args:
            font: A fontTools object representing the font.
            font_path: Font path.
            font_index: Font index.
        Returns:
            A list of supported CMaps.
            - To determine which CMaps are supported, refer to FontParser.get_cmap_encoding().
            - If any Microsoft CMaps are present, only those will be returned.
            - If no Microsoft CMaps are found, the method will only return Macintosh CMaps if they are present.
        """
        microsoft_cmaps: list[CMap] = []
        macintosh_cmaps: list[CMap] = []

        try:
            cmap_tables: list[CmapSubtable] = font["cmap"].tables

            for table in cmap_tables:
                encoding = FontParser.get_cmap_encoding(table.platformID, table.platEncID)
                if encoding is not None:
                    cmap = CMap(table.platformID, table.platEncID)
                    if table.platformID == PlatformID.MICROSOFT:
                        microsoft_cmaps.append(cmap)
                    elif table.platformID == PlatformID.MACINTOSH:
                        macintosh_cmaps.append(cmap)
        except Exception:
            with font_path.open("rb") as f:
                face = Face(f, font_index)

            for charmap in face.charmaps:
                encoding = FontParser.get_cmap_encoding(charmap.platform_id, charmap.encoding_id)
                if encoding is not None:
                    cmap = CMap(charmap.platform_id, charmap.encoding_id)
                    if charmap.platform_id == PlatformID.MICROSOFT:
                        microsoft_cmaps.append(cmap)
                    elif charmap.platform_id == PlatformID.MACINTOSH:
                        macintosh_cmaps.append(cmap)
        return macintosh_cmaps if len(microsoft_cmaps) == 0 else microsoft_cmaps


    @staticmethod
    def get_cmap_encoding(platform_id: int, encoding_id: int) -> Optional[str]:
        """
        Args:
            platform_id: CMap platform id
            encoding_id: CMap encoding id
        Returns:
            The cmap encoding.
            If GDI does not support the platform_id and/or platform_encoding_id, return None.
            Warning, if it return "unknown", it means that the cmap is from a symbol font.
                Call get_symbol_cmap_encoding() to know what is the encoding.
        Notes:
            - GDI only supports all encodings for the Microsoft CMap.
            - For the Macintosh platform, it only supports the platform encoding 1.
        """
        if platform_id in FontParser.CMAP_ENCODING_MAP:
            return FontParser.CMAP_ENCODING_MAP[PlatformID(platform_id)].get(encoding_id, None)
        return None


# The Chinese (cp936 or cp950) and Korean (cp949) aren't in this dict since they doesn't have any unique char.
# This dict have been generated with "proof/[Symbol Font] Find unique char by ansi code page.py"
# The name of those glyph is from this list: https://raw.githubusercontent.com/adobe-type-tools/agl-aglfn/4036a9ca80a62f64f9de4f7321a9a045ad0ecfd6/glyphlist.txt
UNIQUE_ADOBE_GLYPH_NAME_BY_CODE_PAGE: dict[str, set[str]] = {
    "cp874": {'angkhankhuthai', 'lolingthai', 'thanthakhatthai', 'phosamphaothai', 'phophanthai', 'paiyannoithai', 'phinthuthai', 'threethai', 'kokaithai', 'topatakthai', 'lochulathai', 'nonuthai', 'thothungthai', 'lakkhangyaothai', 'ngonguthai', 'thothanthai', 'khokhaithai', 'khokhwaithai', 'oangthai', 'sixthai', 'saraueethai', 'saraaathai', 'wowaenthai', 'chochangthai', 'fourthai', 'maihanakatthai', 'nonenthai', 'maiekthai', 'sosalathai', 'sorusithai', 'saraamthai', 'saraethai', 'saraithai', 'fofanthai', 'fofathai', 'poplathai', 'thothongthai', 'roruathai', 'chochingthai', 'nikhahitthai', 'saraiithai', 'yamakkanthai', 'luthai', 'onethai', 'sosothai', 'maitaikhuthai', 'seventhai', 'khorakhangthai', 'yoyingthai', 'sarauthai', 'dochadathai', 'ruthai', 'maichattawathai',
    'bobaimaithai', 'sarauethai', 'saraaimaimuanthai', 'chochoethai', 'twothai', 'sarauuthai', 'phophungthai', 'saraothai', 'khomutthai', 'thophuthaothai', 'fongmanthai', 'fivethai', 'honokhukthai', 'zerothai', 'maiyamokthai', 'hohipthai', 'khokhonthai', 'ninethai', 'bahtthai', 'saraaethai', 'dodekthai', 'chochanthai', 'eightthai', 'yoyakthai', 'khokhuatthai', 'saraaimaimalaithai', 'maithothai', 'thothahanthai', 'sosuathai', 'saraathai', 'totaothai', 'maitrithai', 'momathai', 'thonangmonthothai'},

    "cp932": {'nekatakanahalfwidth', 'okatakanahalfwidth', 'yukatakanahalfwidth', 'sekatakanahalfwidth', 'hakatakanahalfwidth', 'sakatakanahalfwidth', 'yokatakanahalfwidth', 'mekatakanahalfwidth', 'osmallkatakanahalfwidth', 'sokatakanahalfwidth', 'wakatakanahalfwidth', 'hokatakanahalfwidth', 'ismallkatakanahalfwidth', 'rakatakanahalfwidth', 'katahiraprolongmarkhalfwidth', 'ikatakanahalfwidth', 'nakatakanahalfwidth', 'mikatakanahalfwidth', 'kikatakanahalfwidth', 'tikatakanahalfwidth', 'tusmallkatakanahalfwidth', 'semivoicedmarkkanahalfwidth', 'sikatakanahalfwidth', 'middledotkatakanahalfwidth', 'mokatakanahalfwidth', 'ekatakanahalfwidth', 'hekatakanahalfwidth', 'tekatakanahalfwidth', 'wokatakanahalfwidth', 'makatakanahalfwidth', 'asmallkatakanahalfwidth', 'tokatakanahalfwidth', 'cornerbracketlefthalfwidth', 'mukatakanahalfwidth', 'kukatakanahalfwidth', 'yusmallkatakanahalfwidth', 'yosmallkatakanahalfwidth', 'nokatakanahalfwidth', 'kekatakanahalfwidth', 'takatakanahalfwidth', 'rikatakanahalfwidth', 'ukatakanahalfwidth', 'cornerbracketrighthalfwidth', 'braceleftmid', 'esmallkatakanahalfwidth', 'tukatakanahalfwidth', 'rukatakanahalfwidth', 'nukatakanahalfwidth', 'bracelefttp', 'voicedmarkkanahalfwidth', 'rokatakanahalfwidth', 'kokatakanahalfwidth', 'usmallkatakanahalfwidth', 'bracketleftbt', 'hukatakanahalfwidth', 'kakatakanahalfwidth', 'sukatakanahalfwidth', 'hikatakanahalfwidth', 'periodhalfwidth', 'braceleftbt', 'yasmallkatakanahalfwidth', 'nkatakanahalfwidth', 'rekatakanahalfwidth', 'yakatakanahalfwidth', 'ideographiccommaleft', 'akatakanahalfwidth', 'nikatakanahalfwidth'},

    "cp1250": {'lacute', 'tcedilla', 'dcaron', 'breve', 'lcaron', 'uhungarumlaut', 'racute', 'tcommaaccent', 'ecaron', 'hungarumlaut', 'uring', 'tcaron', 'ncaron', 'rcaron', 'odblacute', 'udblacute', 'ohungarumlaut'},

    "cp1251": {'acyrillic', 'efcyrillic', 'afii10055', 'afii10069', 'afii10097', 'afii10037', 'afii10085', 'afii10053', 'kjecyrillic', 'afii10096', 'afii10019', 'afii10086', 'afii10030', 'afii10034', 'iucyrillic', 'elcyrillic', 'ushortcyrillic', 'afii10052', 'afii10036', 'shchacyrillic', 'iishortcyrillic', 'afii10105', 'afii10061', 'afii10026', 'ercyrillic', 'tecyrillic', 'afii10060', 'afii10106', 'afii10028', 'afii10098', 'afii10042', 'yicyrillic', 'afii10193', 'emcyrillic', 'jecyrillic', 'afii10021', 'afii10054', 'afii10101', 'encyrillic', 'afii10022', 'becyrillic', 'njecyrillic', 'softsigncyrillic', 'afii10075', 'afii10100', 'afii10068', 'afii10089', 'afii10065', 'afii61352', 'iicyrillic', 'iecyrillic', 'afii10088', 'tshecyrillic', 'afii10059', 'vecyrillic', 'zhecyrillic', 'afii10102', 'afii10099', 'iocyrillic', 'pecyrillic', 'afii10050', 'afii10048', 'afii10080', 'gecyrillic', 'afii10035', 'djecyrillic', 'ucyrillic', 'afii10066', 'afii10027', 'afii10045', 'afii10082', 'afii10017', 'afii10076', 'afii10067', 'afii10087', 'iacyrillic', 'afii10024', 'dzhecyrillic', 'afii10058', 'afii10029', 'afii10110', 'afii10084', 'afii10095', 'afii10040', 'yericyrillic', 'afii10072', 'afii10109', 'gjecyrillic', 'ljecyrillic', 'afii10074', 'afii10081', 'dzecyrillic', 'afii10093', 'khacyrillic', 'afii10023', 'afii10079', 'afii10031', 'afii10047', 'escyrillic', 'decyrillic', 'afii10062', 'afii10070', 'afii10049', 'tsecyrillic', 'afii10094', 'afii10025', 'afii10041', 'afii10077', 'afii10073', 'afii10038', 'gheupturncyrillic', 'ereversedcyrillic', 'kacyrillic', 'afii10107', 'afii10108', 'ocyrillic', 'afii10145', 'afii10103', 'afii10032', 'shacyrillic', 'checyrillic', 'afii10090', 'numero', 'zecyrillic', 'afii10104', 'afii10092', 'afii10083', 'afii10056', 'afii10039', 'hardsigncyrillic', 'afii10044', 'afii10078', 'afii10018', 'icyrillic', 'afii10043', 'afii10091', 'afii10046', 'afii10057', 'afii10051', 'afii10071', 'ecyrillic', 'afii10020', 'afii10033'},

    "cp1252": {'thorn', 'eth'},

    "cp1253": {'sigmafinal', 'iotatonos', 'pi', 'kappa', 'dieresistonos', 'lambda', 'chi', 'sigma', 'delta', 'psi', 'rho', 'sigma1', 'epsilontonos', 'alphatonos', 'epsilon', 'beta', 'deltagreek', 'zeta', 'iotadieresis', 'upsilontonos', 'afii00208', 'omicrontonos', 'iota', 'alpha', 'omega', 'omicron', 'gamma', 'upsilon', 'omegagreek', 'tonos', 'omegatonos', 'upsilondieresistonos', 'theta', 'nu', 'dialytikatonos', 'phi', 'mu', 'etatonos', 'iotadieresistonos', 'tau', 'upsilondieresis', 'horizontalbar', 'xi', 'eta', 'mugreek'},

    "cp1254": {'gbreve', 'dotlessi', 'idot', 'idotaccent'},

    "cp1255": {'daletsegol', 'het', 'vav', 'reshhatafpatahhebrew', 'reshtserehebrew', 'zayinhebrew', 'tsere12', 'hatafsegolhebrew', 'reshholam', 'afii57678', 'tsere', 'qamatsqatanhebrew', 'daletpatah', 'qamatsqatanquarterhebrew', 'daletholamhebrew', 'finaltsadi', 'afii57668', 'pehebrew', 'mem', 'afii57803', 'qubutsquarterhebrew', 'rafe', 'qamats', 'hiriqhebrew', 'qoftsere', 'hatafsegol30', 'zayin', 'hiriqquarterhebrew', 'afii57670', 'afii57671', 'afii57801', 'afii57636', 'hatafqamats34', 'patahquarterhebrew', 'qamatswidehebrew', 'dalethiriq', 'qubuts31', 'afii57672', 'hehebrew', 'qofsegolhebrew', 'afii57680', 'holamquarterhebrew', 'reshqamats', 'afii57717', 'qofpatahhebrew', 'qofhiriq', 'tserehebrew', 'hiriq', 'qubutshebrew', 'kafhebrew', 'nun', 'afii57689', 'shindothebrew', 'afii57793', 'qubuts18', 'pe', 'memhebrew', 'yodhebrew', 'daletpatahhebrew', 'finalmemhebrew', 'finalpehebrew', 'hatafsegolquarterhebrew', 'qamatsqatannarrowhebrew', 'afii57645', 'shevaquarterhebrew', 'dalethebrew', 'patahwidehebrew', 'dalethatafsegol', 'lamedholamdageshhebrew', 'afii57664', 'shevahebrew', 'afii57842', 'finalkafsheva', 'tsere1e', 'hiriqnarrowhebrew', 'sheva22', 'tethebrew', 'hatafqamats28', 'hatafqamats', 'segolnarrowhebrew', 'afii57804', 'gershayimhebrew', 'tav', 'nunhebrew', 'holamhebrew', 'afii57716', 'patahnarrowhebrew', 'he', 'rafehebrew', 'qofsegol', 'afii57687', 'hatafqamatsnarrowhebrew', 'qofqamatshebrew', 'dalet', 'qubutswidehebrew', 'vavhebrew', 'qofshevahebrew', 'gimelhebrew', 'dalethiriqhebrew', 'patah', 'sheqelhebrew', 'qofholam', 'ayinhebrew', 'segol13', 'reshhebrew', 'finalnun', 'newsheqelsign', 'hatafsegol', 'hatafsegol24', 'sofpasuqhebrew', 'qamats1c', 'dalethatafpatah', 'reshshevahebrew', 'sheva2e', 'reshhatafsegolhebrew', 'afii57839', 'afii57681', 'hatafqamatsquarterhebrew', 'afii57667', 'lamedhebrew', 'qofpatah', 'tserewidehebrew', 'finalnunhebrew', 'sheva', 'daletqubutshebrew', 'finaltsadihebrew', 'qamatsde', 'tsadihebrew', 'finalkafshevahebrew', 'hatafqamatswidehebrew', 'reshhatafpatah', 'afii57794', 'reshqubuts', 'samekh', 'sheqel', 'finalpe', 'shevawidehebrew', 'segol', 'reshhiriq',
    'holamwidehebrew', 'qamatsquarterhebrew', 'lamedholamhebrew', 'afii57841', 'vavyodhebrew', 'hatafqamats1b', 'hatafsegolnarrowhebrew', 'afii57795', 'hatafpatahhebrew', 'qofhatafpatah', 'finalkafqamats', 'shinhebrew', 'afii57684', 'reshqamatshebrew', 'hatafqamatshebrew', 'afii57806', 'shevanarrowhebrew', 'sindothebrew', 'patah2a', 'segolhebrew', 'afii57798', 'qofhatafpatahhebrew', 'afii57800', 'qamatsqatanwidehebrew', 'hiriq14', 'qofqubuts', 'hatafpatah', 'hatafpatahnarrowhebrew', 'reshholamhebrew', 'afii57675', 'samekhhebrew', 'shin', 'tavhebrew', 'holam', 'finalkafhebrew', 'finalkafqamatshebrew', 'afii57679', 'tserequarterhebrew', 'holamnarrowhebrew', 'hatafsegolwidehebrew', 'qamatsnarrowhebrew', 'segolquarterhebrew', 'hatafpatahwidehebrew', 'tet', 'hiriq21', 'qamats27', 'afii57674', 'dalethatafpatahhebrew', 'bet', 'bethebrew', 'afii57685', 'yod', 'lamedholamdagesh', 'gereshhebrew', 'alef', 'daletqubuts', 'segol2c', 'qoftserehebrew', 'afii57677', 'finalkaf', 'daletqamatshebrew', 'ayin', 'hatafpatah16', 'paseqhebrew', 'qubuts25', 'tsere2b', 'afii57802', 'afii57669', 'dalethatafsegolhebrew', 'qofhatafsegolhebrew', 'daletqamats', 'qofholamhebrew', 'qamats10', 'afii57718', 'yodyodhebrew', 'afii57807', 'afii57799', 'qofhiriqhebrew', 'qofqubutshebrew', 'tsadi', 'qubutsnarrowhebrew', 'maqafhebrew', 'reshsegolhebrew', 'holam26', 'sheva15', 'lamedholam', 'vavvavhebrew', 'reshqubutshebrew', 'patah11', 'patah1d', 'kaf', 'daletshevahebrew', 'qamats1a', 'sheva115', 'dalettserehebrew', 'qofsheva', 'hethebrew', 'segol1f', 'hiriq2d',
    'afii57673', 'afii57797', 'dalettsere', 'qofhebrew', 'hiriqwidehebrew', 'reshhiriqhebrew', 'tserenarrowhebrew', 'patahhebrew', 'reshhatafsegol', 'daletholam', 'reshpatah', 'qubuts', 'afii57665', 'hatafpatah23', 'afii57658', 'gimel', 'daletsheva', 'hatafpatahquarterhebrew', 'alefhebrew', 'siluqlefthebrew', 'reshsegol', 'qofqamats', 'hatafsegol17', 'afii57676', 'afii57688', 'lamed', 'qof', 'reshpatahhebrew', 'afii57683', 'segolwidehebrew', 'finalmem', 'qofhatafsegol', 'dageshhebrew', 'afii57686', 'qamatshebrew', 'qamats33', 'qamats29', 'afii57682', 'daletsegolhebrew', 'reshtsere', 'holam32', 'afii57690', 'afii57666', 'dagesh', 'holam19', 'siluqhebrew', 'afii57796', 'resh', 'reshsheva', 'hatafpatah2f'},

    "cp1256": {'afii57449', 'afii57440', 'afii57450', 'beharabic', 'afii57419', 'sadarabic', 'meemarabic', 'afii57508', 'afii57512', 'semicolonarabic', 'afii57423', 'dadarabic', 'taharabic', 'afii57442', 'afii57513', 'afii57448', 'gafarabic', 'ddalarabic', 'afii57446', 'afii57441', 'afii57430', 'lamarabic', 'afii57470', 'afii57421', 'dammalowarabic', 'alefmaksuraarabic', 'hamzadammaarabic',
    'afii57426', 'noonarabic', 'dammatanarabic', 'zerowidthnonjoiner', 'tehmarbutaarabic', 'qafarabic', 'hamzaarabic', 'afii57454', 'hamzafathatanarabic', 'dalarabic', 'jeemarabic', 'afii57506', 'afii57458', 'afii57445', 'rehyehaleflamarabic', 'hamzalowkasraarabic', 'afii57519', 'afii57412', 'noonghunnaarabic', 'hamzasukunarabic', 'shaddafathatanarabic', 'zainarabic', 'afii57444', 'alefhamzabelowarabic', 'feharabic', 'fathaarabic', 'afii61664', 'afii57415', 'afii57403', 'kashidaautoarabic', 'afii57422', 'wawarabic', 'afii57409', 'sukunarabic', 'kafarabic', 'tcheharabic', 'afii57453', 'afii57433', 'yeharabic', 'jeharabic', 'hehaltonearabic', 'afii57411', 'alefmaddaabovearabic', 'afii57432', 'alefhamzaabovearabic', 'afii57511', 'afii57414', 'hamzadammatanarabic', 'shaddaarabic', 'khaharabic', 'rreharabic', 'kashidaautonosidebearingarabic', 'kasratanarabic', 'teharabic', 'peharabic', 'afii57429', 'afii57452', 'hamzalowkasratanarabic', 'haaltonearabic', 'heharabic', 'fathatanarabic', 'questionarabic', 'kasraarabic', 'afii57420', 'afii57418', 'tatweelarabic', 'fathalowarabic', 'afii57451', 'afii57507', 'afii57455', 'wawhamzaabovearabic', 'afii57416', 'dammatanaltonearabic', 'afii57424', 'afii57410', 'afii57388', 'thalarabic', 'afii57443', 'haharabic', 'commaarabic', 'afii57413', 'sheenarabic', 'ainarabic', 'afii57417', 'hamzafathaarabic', 'yehhamzaabovearabic', 'afii57456', 'afii57428', 'afii57425', 'alefarabic', 'zaharabic', 'tteharabic', 'hamzalowarabic', 'ghainarabic', 'afii57514', 'reharabic', 'yehbarreearabic', 'afii57509', 'afii301', 'dammaarabic', 'afii57427', 'afii57457', 'afii57431', 'afii57407', 'seenarabic', 'afii57434', 'theharabic'},

    "cp1257": {'ncommaaccent', 'rcedilla', 'lcedilla', 'emacron', 'ncedilla', 'iogonek', 'edotaccent', 'kcommaaccent', 'amacron', 'uogonek', 'gcommaaccent', 'kcedilla', 'rcommaaccent', 'umacron', 'gcedilla', 'omacron', 'edot', 'imacron', 'lcommaaccent'},

    "cp1258": {'tildecmb', 'gravecomb', 'dong', 'acutecmb', 'gravecmb', 'dotbelowcmb', 'uhorn', 'acutecomb', 'hookcmb', 'ohorn', 'hookabovecomb', 'tildecomb', 'dotbelowcomb'}
}
