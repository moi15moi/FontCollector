from __future__ import annotations
import logging
import os
import shutil
from .._version import __version__
from .abc_font_face import ABCFontFace
from .factory_abc_font_face import FactoryABCFontFace
from .normal_font_face import NormalFontFace
from .font_loader import FontLoader
from .font_parser import FontParser
from .font_type import FontType
from .name import NameID
from .variable_font_face import VariableFontFace
from datetime import date
from fontTools.ttLib.ttCollection import TTCollection
from fontTools.ttLib.ttFont import TTFont
from fontTools.varLib import instancer
from pathlib import Path
from typing import Iterable, Sequence, Set

_logger = logging.getLogger(__name__)


class Helpers:

    @staticmethod
    def copy_font_to_directory(
        fonts: Iterable[ABCFontFace],
        output_directory: Path,
        create_directory_if_doesnt_exist: bool = True,
        convert_variable_font_into_truetype_collection: bool = True,
    ) -> None:
        """
        Parameters:
            fonts (Iterable[ABCFont]): An list, set or 
            output_directory (Path): The directory where the font are going to be save
            create_directory_if_doesnt_exist (bool):
                If true and the output_directory doesn't exist, it will be created
                If false and the output_directory doesn't exist, an exception will be raised
            convert_variable_font_into_truetype_collection (bool):
                If true, it will convert the variable font into an truetype collection font
                    It is usefull, because libass doesn't support variation font: https://github.com/libass/libass/issues/386
                    It convert it in a format that libass support
                If false, it won't do anything special. The variable font will be copied like any other font.
        """

        # TODO rework this method

        if not os.path.exists(output_directory) and create_directory_if_doesnt_exist:
            os.makedirs(output_directory)

        for font in fonts:

            if isinstance(font, VariableFontFace):
                font_name = font.get_family_prefix_from_lang("en")
                if len(font_name) == 0:
                    # Get an random families_prefix
                    font_name = list(font.families_prefix)[0].value
                else:
                    font_name = font_name[0].value
            elif isinstance(font, NormalFontFace):
                font_name = font.get_exact_name_from_lang("en")
                if len(font_name) == 0:
                    # Get an random family_names
                    font_name = list(font.family_names)[0].value
                else:
                    font_name = font_name[0].value
            else:
                raise NotImplementedError(f"The font type {type(font)} hasn't been implemented. Open an issue on Github.")


            if isinstance(font, VariableFontFace) and convert_variable_font_into_truetype_collection:
                font_filename = os.path.join(output_directory, f"{font.families_prefix}.ttc")
                Helpers.variable_font_to_collection(font.filename, font.font_index, font_filename)
            else:
                if font.font_type == FontType.OPENTYPE:
                    file_extension = ".otf"
                elif font.font_type == FontType.TRUETYPE:
                    file_extension = ".ttf"
                else:
                    raise NotImplementedError(f"The font type {font.font_type} doesn't have any file extension.")

                font_filename = os.path.join(output_directory, f"{font_name}{file_extension}")                
                # Don't overwrite fonts
                if not os.path.isfile(font_filename):
                    shutil.copy(font.filename, font_filename)