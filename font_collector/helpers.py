import logging
import os
import shutil
from .ass_style import AssStyle
from .parse_font import ParseFont
from .font import Font
from .font_loader import FontLoader
from .font_result import FontResult
from ._version import __version__
from datetime import date
from fontTools.ttLib.ttFont import TTFont
from fontTools.ttLib.ttCollection import TTCollection
from fontTools.varLib import instancer
from pathlib import Path
from typing import List, Set, Tuple, Union

_logger = logging.getLogger(__name__)


class Helpers:
    @staticmethod
    def get_used_font_by_style(
        font_collection: Set[Font], style: AssStyle, search_by_family_name: bool = True
    ) -> Union[FontResult, None]:
        """
        Parameters:
            fontCollection (Set[Font]): Font collection
            style (AssStyle): An AssStyle
            search_by_family_name (bool):
                If true, it will search the font by it's family name.
                If false, it will search the font by it's exact_name (fullname or postscript name).
        Returns:
            Ordered list of the font that match the best to the AssStyle
        """
        fonts_match: List[Tuple[int, Font]] = []

        for font in font_collection:
            if (search_by_family_name and style.fontname in font.family_names) or (
                not search_by_family_name and style.fontname in font.exact_names
            ):

                weight_compare = abs(style.weight - font.weight)

                if (style.weight - font.weight) > 150:
                    weight_compare -= 120

                # Thanks to rcombs@github: https://github.com/libass/libass/issues/613#issuecomment-1102994528
                weight_compare = (
                    ((((weight_compare << 3) + weight_compare) << 3)) + weight_compare
                ) >> 8

                fonts_match.append((weight_compare, font))

        # The last sort parameter (font.weight) is totally optional. In VSFilter, when the weightCompare is the same, it will take the first one, so the order is totally random, so VSFilter will not always display the same font.
        # We also priorize Truetype/Opentype font over variable fonts
        fonts_match.sort(
            key=lambda font: (
                font[0],
                -(style.italic == font[1].italic),
                font[1].is_var,
                font[1].weight,
            )
        )

        if len(fonts_match) > 0:
            match = fonts_match[0][1]
            mismatch_italic = not (match.italic == style.italic)
            mismatch_bold = not (-150 < match.weight - style.weight < 150)

            font_result = FontResult(match, mismatch_bold, mismatch_italic)
            _logger.info(f"Found '{style.fontname}' at '{font_result.font.filename}'")
            return font_result
        elif search_by_family_name:
            return Helpers.get_used_font_by_style(
                font_collection, style, search_by_family_name=False
            )
        else:
            _logger.error(f"Could not find font '{style.fontname}'")
            return None

    @staticmethod
    def copy_font_to_directory(
        font_collection: Set[Font],
        output_directory: Path,
        create_directory_if_doesnt_exist: bool = True,
        convert_variable_font_into_truetype_collection: bool = True,
    ):
        """
        Parameters:
            font_collection (Set[Font]): Font collection
            output_directory (Path): The directory where the font are going to be save
            create_directory_if_doesnt_exist (bool): If true and the output_directory doesn't exist, it will be created
                                                     If false and the output_directory doesn't exist, an exception will be raised
        """

        if not os.path.exists(output_directory) and create_directory_if_doesnt_exist:
            os.makedirs(output_directory)

        for font in font_collection:

            if font.is_var and convert_variable_font_into_truetype_collection:
                # We take the first result, but it doesn't matter
                font = Helpers.variable_font_to_collection(font.filename, os.getcwd())[
                    0
                ]

            # Don't overwrite fonts
            if not os.path.isfile(
                os.path.join(output_directory, Path(font.filename).name)
            ):
                shutil.copy(font.filename, output_directory)

    @staticmethod
    def variable_font_to_collection(
        fontpath: str, outputDirectory: str, cache_generated_font: bool = True
    ) -> List[Font]:
        """
        Parameters:
            font (Font): The variable font that need to be converted
            outputDirectory (str): Path where to save the generated font
            cache_generated_font (bool):  Converting an variable font into an collection font is a slow process. Caching the result boost the performance.
                If true, then the generated font will be cached.
                If false, then the generated font won't be cached.
        Returns:
            List of generated fonts that represent the truetype collection font generated
        """
        font_collection = TTCollection()
        ttFont = TTFont(fontpath)

        family_prefix = ParseFont.get_var_font_family_prefix(ttFont)

        for instance in ttFont["fvar"].instances:
            generated_font = instancer.instantiateVariableFont(
                ttFont, instance.coordinates
            )

            axis_value_tables = ParseFont.get_axis_value_from_coordinates(
                ttFont, instance.coordinates
            )
            family_name, full_font_name = ParseFont.get_var_font_family_fullname(
                ttFont, axis_value_tables
            )

            generated_font["name"].setName(family_name, 1, 3, 1, 0x409)
            generated_font["name"].setName(full_font_name, 2, 3, 1, 0x409)
            generated_font["name"].setName(
                f"FontCollector v {__version__}:{full_font_name}:{date.today()}",
                3,
                3,
                1,
                0x409,
            )
            generated_font["name"].setName(full_font_name, 4, 3, 1, 0x409)

            font_collection.fonts.append(generated_font)

        savepath = os.path.join(outputDirectory, f"{family_prefix}.ttc")
        font_collection.save(savepath)

        if cache_generated_font:
            for font in font_collection:
                FontLoader.add_generated_font(font)

        return Font.from_font_path(savepath)
