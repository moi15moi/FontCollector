import logging
from ..exceptions import InvalidFontException, InvalidVariableFontException
from .font_type import FontType
from .name import Name, NameID, PlatformID
from io import BufferedReader
from itertools import product
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from fontTools.ttLib.ttFont import TTFont
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
from fontTools.ttLib.tables._n_a_m_e import NameRecord
from fontTools.varLib.instancer.names import ELIDABLE_AXIS_VALUE_NAME
from freetype import Face
from freetype.ft_enums.ft_style_flags import FT_STYLE_FLAGS
from langcodes import Language
from struct import error as struct_error

_logger = logging.getLogger(__name__)


class FontParser:
    DEFAULT_WEIGHT = 400
    DEFAULT_ITALIC = False

    CMAP_ENCODING_MAP = {
        PlatformID.MACINTOSH: {
            0: "mac_roman",
        },
        PlatformID.MICROSOFT: {
            0: "utf_16_be",
            1: "utf_16_be",
            2: "cp932",
            3: "cp936",
            4: "cp950",
            5: "cp949",
            6: "cp1361",
            10: "utf_16_be",
        },
    }


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
        
        if font["STAT"].table.DesignAxisRecord is None:
            raise InvalidVariableFontException("The font has a stat table, but it doesn't have any DesignAxisRecord")

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
    def get_var_font_family_prefix(names: List[NameRecord], platform_id: PlatformID) -> Set[Name]:
        """
        This method is inspired by how GDI parse Variable Fonts.
        Parameters:
            font (TTFont): An fontTools object
        Returns:
            The family name prefix.
        """
        family_prefix = FontParser.get_filtered_names(names, platformID=platform_id, nameID=NameID.TYPOGRAPHIC_FAMILY_NAME)
        
        if not family_prefix:
            family_prefix = FontParser.get_filtered_names(names, platformID=platform_id, nameID=NameID.FAMILY_NAME)

        return family_prefix

    @staticmethod
    def get_distance_between_axis_value_and_coordinates(
        font: TTFont, coordinates: Dict[str, float], axis_value: Any, axis_format: int
    ) -> float:
        """
        This method is inspired by how GDI parse Variable Fonts.
        You should call FontParser.is_valid_variable_font before calling this method.

        Parameters:
            ttfont (TTFont): An fontTools object
            coordinates (Dict[str, float]): The coordinates of an NamedInstance in the fvar table.
            axis_value (Any): An AxisValue
            axis_format (int): The AxisValue Format.
                Since the AxisValue from AxisValueRecord of an AxisValue Format 4 doesn't contain an Format attribute, this parameter is needed.
        Returns:
            The distance between_axis_value_and_coordinates
        """
        try:
            axis_tag = font["STAT"].table.DesignAxisRecord.Axis[axis_value.AxisIndex].AxisTag
        except IndexError:
            raise InvalidVariableFontException(f"The DesignAxisRecord doesn't contain an axis at the index {axis_value.AxisIndex}")

        # If the coordinates cannot be found, default to 0
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
    def get_axis_value_from_coordinates(ttfont: TTFont, coordinates: Dict[str, float]) -> List[Any]:
        """
        You should call FontParser.is_valid_variable_font before calling this method.

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
        is_axis_useds: List[bool] = [False] * len(ttfont["STAT"].table.DesignAxisRecord.Axis)

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
        ttfont: TTFont, axis_values: List[Any]
    ) -> Tuple[Set[Name], Set[Name], float, bool]:
        """
        You should call FontParser.is_valid_variable_font before calling this method.

        Parameters:
            ttfont (TTFont): An fontTools object
            axis_values (List[Any]): An list of AxisValue.
            family_name_prefix (Name): The variable family name prefix.
                Ex: For the name "Alegreya Italic", "Alegreya" is the family name prefix.
        Returns:
            An family_name, full_name, weight, italic that represent the axis_values.
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

        weight = FontParser.DEFAULT_WEIGHT
        italic = FontParser.DEFAULT_ITALIC

        axis_values_names: List[Set[Name]] = []
        family_name_axis_value_index: List[bool] = [False] * len(axis_values)
        fullname_axis_value_index: List[bool] = [False] * len(axis_values)


        for i, axis_value in enumerate(axis_values):

            axis_value_name = FontParser.get_filtered_names(ttfont["name"].names, platformID=PlatformID.MICROSOFT, nameID=axis_value.ValueNameID)
            if not axis_value_name:
                raise InvalidVariableFontException("An axis value has an invalid ValueNameID")
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

                if ttfont["STAT"].table.DesignAxisRecord.Axis[axis_index].AxisTag == "wght":
                    weight = value
                elif ttfont["STAT"].table.DesignAxisRecord.Axis[axis_index].AxisTag == "ital":
                    italic = value == 1

                if not (axis_value.Flags & ELIDABLE_AXIS_VALUE_NAME):
                    fullname_axis_value_index[i] = True

                    use_in_family_name = True
                    if ttfont["STAT"].table.DesignAxisRecord.Axis[axis_index].AxisTag == "wght":
                        use_in_family_name = value not in (400, 700)
                    elif ttfont["STAT"].table.DesignAxisRecord.Axis[axis_index].AxisTag == "ital":
                        use_in_family_name = value not in (0, 1)

                    if use_in_family_name:
                        family_name_axis_value_index[i] = True

        family_name = set()
        fullname = set()
        
        # Generate family_name an fullname
        for item in product(*axis_values_names):
            langs: Set[Language] = set()
            for element in item:
                langs.add(element.lang_code)

            family_name_str = " ".join([element.value for i, element in enumerate(item) if family_name_axis_value_index[i]])
            fullname_str = " ".join([element.value for i, element in enumerate(item) if fullname_axis_value_index[i]])

            family_name.update({Name(family_name_str, lang) for lang in langs})
            fullname.update({Name(fullname_str, lang) for lang in langs})
        
        # An element in the family_name haven't be found
        if not family_name:
            family_name = set([Name("", Language.get("en"))])


        if all(not element for element in fullname_axis_value_index):
            # Fallback if all the element have the flag ELIDABLE_AXIS_VALUE_NAME
            if hasattr(ttfont['STAT'].table, "ElidedFallbackNameID"):
                elided_fallback_name = FontParser.get_filtered_names(ttfont['name'].names, platformID=PlatformID.MICROSOFT, nameID=ttfont['STAT'].table.ElidedFallbackNameID)
            
                if elided_fallback_name:
                    fullname = elided_fallback_name
                else:
                    # The elided_fallback_name haven't been found
                    weight = FontParser.DEFAULT_WEIGHT
                    italic = FontParser.DEFAULT_ITALIC
                    fullname = set([Name(f"Regular", Language.get("en"))])
            else:
                fullname = set([Name(f"Normal", Language.get("en"))])


        return family_name, fullname, weight, italic


    @staticmethod
    def get_filtered_names(
        names_record: List[NameRecord], 
        platformID: Optional[PlatformID] = None, 
        platEncID: Optional[int] = None, 
        nameID: Optional[NameID] = None, 
        langID: Optional[int] = None
    ) -> Set[Name]:
        """
        Parameters:
            names_record (List[NameRecord]): Naming table
            platformID (Optional[int]): Filtered the names_record by platformID
            platEncID (Optional[int]): Filtered the names_record by platEncID
            nameID (Optional[int]): Filtered the names_record by nameID
            langID (Optional[int]): Filtered the names_record by langID
        Returns:
            A list of the decoded NameRecord
        """
        names: set[Name] = set()

        for name_record in names_record:
            if (
                (platformID is None or name_record.platformID == platformID) and 
                (platEncID is None or name_record.platEncID == platEncID) and 
                (nameID is None or name_record.nameID == nameID) and 
                (langID is None or name_record.langID == langID)
            ):
                names.add(Name.from_name_record(name_record))

        return names


    @staticmethod
    def get_font_italic_bold_property_with_freetype(
        font_path: str, font_index: int
    ) -> Tuple[bool, bool, int]:
        """
        Parameters:
            font_path (str): Font path.
            font_index (int): Font index.
        Returns:
            is_italic, is_glyphs_emboldened, weight
        """

        font = Face(Path(font_path).open("rb"), font_index)
        is_italic = bool(font.style_flags & FT_STYLE_FLAGS["FT_STYLE_FLAG_ITALIC"])
        is_glyphs_emboldened = bool(font.style_flags & FT_STYLE_FLAGS["FT_STYLE_FLAG_BOLD"])
        weight = 700 if is_glyphs_emboldened else 400

        return is_italic, is_glyphs_emboldened, weight


    @staticmethod
    def get_font_italic_bold_property_microsoft_platform(
        font: TTFont, font_path: str, font_index: int
    ) -> Tuple[bool, bool, int]:
        """
        Parameters:
            font (TTFont): An fontTools object
            font_path (str): Font path.
            font_index (int): Font index.
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
        font: TTFont, font_path: str, font_index: int
    ) -> Tuple[bool, int]:
        """
        Parameters:
            font (TTFont): An fontTools object
            font_path (str): Font path.
            font_index (int): Font index.
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
    def get_supported_cmaps(cmap_tables: List[CmapSubtable]) -> List[CmapSubtable]:
        """
        Parameters:
            cmap_tables (List[CmapSubtable]): A list of Cmap.
        Returns:
            A list of the supported Cmap.
            GDI support microsoft cmap and if there is no microsoft cmap, it also support roman mac cmap.
        """

        valid_cmaps = list(filter(lambda table: table.platformID == PlatformID.MICROSOFT, cmap_tables))

        # GDI seems to take apple cmap if there isn't any microsoft cmap: https://github.com/libass/libass/issues/679
        if len(valid_cmaps) == 0:
            valid_cmaps = list(filter(lambda table: table.platformID == PlatformID.MACINTOSH and table.platEncID == 0, cmap_tables))
        
        return valid_cmaps


    @staticmethod
    def get_cmap_encoding(cmap_table: CmapSubtable) -> Optional[str]:
        """
        Parameters:
            cmap_table (CmapSubtable): CMAP table
        Returns:
            The cmap codepoint encoding.
            If GDI does not support the platform_id and/or platform_encoding_id, return None.
        """
        return FontParser.CMAP_ENCODING_MAP.get(cmap_table.platformID, {}).get(cmap_table.platEncID, None)