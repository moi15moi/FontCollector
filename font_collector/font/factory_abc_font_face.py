from __future__ import annotations
import logging
from ..exceptions import InvalidFontException, InvalidNormalFontFaceException, InvalidVariableFontFaceException
from .abc_font_face import ABCFontFace
from .normal_font_face import NormalFontFace
from .font_parser import FontParser
from .font_type import FontType
from .name import NameID, PlatformID
from .variable_font_face import VariableFontFace
from pathlib import Path
from fontTools.ttLib.ttFont import TTFont
from os import linesep
from typing import Any

_logger = logging.getLogger(__name__)


class FactoryABCFontFace:
    @staticmethod
    def from_font_path(font_path: Path) -> tuple[list[ABCFontFace], bool]:
        """
        Args:
            font_path: Font path. The font can be a .ttf, .otf, .ttc or .otc file
        Returns:
            A tuple containing a list of NormalFontFace or VariableFontFace objects representing the font file
            at the given path and a boolean indicating whether the font is a collection font (TTC/OTC fonts)
        """
        ttFonts: list[TTFont] = []

        font = TTFont(font_path, fontNumber=0)
        ttFonts.append(font)

        is_collection_font = False

        # Handle TTC/OTC font
        if hasattr(font.reader, "numFonts"):
            is_collection_font = True
            if font.reader.numFonts > 1:
                for index in range(1, font.reader.numFonts):
                    font = TTFont(font_path, fontNumber=index)
                    ttFonts.append(font)

        fonts: list[ABCFontFace] = []
        try:
            for font_index, ttFont in enumerate(ttFonts):

                # If is Variable Font, else "normal" font
                is_var_font = FontParser.is_valid_variable_font(ttFont)
                if is_var_font:
                    try:
                        fonts.extend(FactoryABCFontFace.__create_variable_fonts(ttFont, font_index))
                    except InvalidVariableFontFaceException:
                        is_var_font = False

                if not is_var_font:
                    font = FactoryABCFontFace.__create_font(ttFont, font_path, font_index)
                    fonts.append(font)
        except InvalidFontException:
            _logger.error(f'The font "{font_path}" is invalid.{linesep}If you think it is an error, please open an issue on github, share the font and the following error message:')
            raise
        except Exception:
            _logger.error(f'An unknown error occurred while reading the font "{font_path}"{linesep}Please open an issue on github, share the font and the following error message:')
            raise

        return fonts, is_collection_font


    @staticmethod
    def __create_font(ttFont: TTFont, font_path: Path, font_index: int) -> NormalFontFace:
        """
        Args:
            ttFont: An fontTools object
            font_path: Font path.
            font_index: Font index.
        Returns:
            An FontFace instance that represent the ttFont.
        """
        cmaps = FontParser.get_supported_cmaps(ttFont, font_path, font_index)
        if len(cmaps) == 0:
             raise InvalidNormalFontFaceException(f"The font doesn't contain any valid cmap.")

        cmap_platform_id = cmaps[0].platform_id
        family_names = FontParser.get_filtered_names(ttFont["name"].names, platformID=cmap_platform_id, nameID=NameID.FAMILY_NAME)

        font_type = FontType.from_font(ttFont)
        if font_type == FontType.TRUETYPE:
            exact_names = FontParser.get_filtered_names(ttFont["name"].names, platformID=cmap_platform_id, nameID=NameID.FULL_NAME)
        elif font_type == FontType.OPENTYPE:
            exact_names = FontParser.get_filtered_names(ttFont["name"].names, platformID=cmap_platform_id, nameID=NameID.POSTSCRIPT_NAME)
        elif font_type == FontType.UNKNOWN:
            raise InvalidNormalFontFaceException(f"The font type is not recognized.")
        else:
            raise InvalidNormalFontFaceException(f"The font isn't an opentype or truetype. It is {font_type.name}")


        if cmap_platform_id == PlatformID.MICROSOFT:
            is_italic, is_glyphs_emboldened, weight = FontParser.get_font_italic_bold_property_microsoft_platform(ttFont, font_path, font_index)
        elif cmap_platform_id == PlatformID.MACINTOSH:
            is_italic, is_glyphs_emboldened, weight = FontParser.get_font_italic_bold_property_mac_platform(ttFont, font_path, font_index)
        else:
            # This should never happen
             raise InvalidNormalFontFaceException(f"The font {font_path} doesn't contain any valid cmap.")


        return NormalFontFace(
            font_index,
            family_names,
            exact_names,
            weight,
            is_italic,
            is_glyphs_emboldened,
            font_type
        )


    def __create_variable_fonts(ttFont: TTFont, font_index: int) -> list[VariableFontFace]:
        """
        Args:
            ttFont: An fontTools object
            font_index: Font index.
        Returns:
            An list of Font instance that represent the ttFont.
        """

        fonts: set[VariableFontFace] = set()
        # GDI support only microsoft variable font
        families_prefix = FontParser.get_var_font_family_prefix(ttFont["name"].names, PlatformID.MICROSOFT)

        font_type = FontType.from_font(ttFont)
        if font_type == FontType.UNKNOWN:
            raise InvalidVariableFontFaceException(f"The font type is not recognized.")
        elif font_type not in (FontType.TRUETYPE, FontType.OPENTYPE):
            raise InvalidVariableFontFaceException(f"The font isn't an opentype or truetype. It is {font_type.name}")

        # Ex axis_values_coordinates: [([AxisValue], {"wght", 400.0})]
        axis_values_coordinates: list[tuple[list[Any], dict[str, float]]] = []

        for instance in ttFont["fvar"].instances:
            axis_value_table = FontParser.get_axis_value_from_coordinates(ttFont, instance.coordinates)

            # If we get exactly the same axis_value_table for 2 different fvar instance, then, we ignore the first fvar instance.
            named_instance_coordinates = instance.coordinates
            for axis_value_coordinates in axis_values_coordinates:
                if axis_value_coordinates[0] == axis_value_table:
                    named_instance_coordinates = axis_value_coordinates[1]
                    break
            axis_values_coordinates.append((axis_value_table, instance.coordinates))

            (
                families_suffix,
                exact_names_suffix,
                weight,
                is_italic,
            ) = FontParser.get_axis_value_table_property(
                ttFont, axis_value_table
            )

            font = VariableFontFace(
                font_index,
                families_prefix,
                families_suffix,
                exact_names_suffix,
                int(weight),
                is_italic,
                font_type,
                named_instance_coordinates,
            )
            fonts.add(font)

        return list(fonts)
