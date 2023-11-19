import logging
import os
import shutil
from .._version import __version__
from .abc_font import ABCFont
from .factory_abc_font import FactoryABCFont
from .font import Font
from .font_loader import FontLoader
from .font_parser import FontParser
from .font_type import FontType
from .name import NameID
from .variable_font import VariableFont
from datetime import date
from fontTools.ttLib.ttCollection import TTCollection
from fontTools.ttLib.ttFont import TTFont
from fontTools.varLib import instancer
from pathlib import Path
from typing import Iterable, Sequence, Set

_logger = logging.getLogger(__name__)


class Helpers:

    @staticmethod
    def variable_font_to_collection(filename: str, font_index: int, save_path: str, cache_generated_font: bool = True
    ) -> None:
        """
        Parameters:
            filename (str): The path to the variable font that need to be converted.
            font_index (int): Font index.
            save_path (str): Path where to save the generated font
            cache_generated_font (bool):  Converting an variable font into an collection font is a slow process. Caching the result boost the performance.
                If true, then the generated font will be cached.
                If false, then the generated font won't be cached.
        Returns:
            List of Font that represent the truetype collection font generated
        """

        if os.path.isfile(save_path):
            raise FileExistsError(f'There is already a font at "{save_path}"')

        font_collection = TTCollection()
        ttFont = TTFont(filename, fontNumber=font_index)
        fonts = FactoryABCFont.from_font_path(filename)
        
        # Only conserve the right font_index
        fonts = list(filter(lambda font: font.font_index == font_index, fonts))

        if len(fonts) == 0:
            raise ValueError(f"There is no valid font at the index {font_index}")

        cmaps = FontParser.get_supported_cmaps(ttFont, filename, font_index)


        for font in fonts:
            if not isinstance(font, VariableFont):
                raise ValueError(f"The font {filename} isn't an variable font")
            generated_font = instancer.instantiateVariableFont(ttFont, font.named_instance_coordinates)

            for cmap in cmaps:
                for family_name in font.family_names:
                    generated_font["name"].setName(family_name.value, NameID.FAMILY_NAME, cmap.platform_id, cmap.platform_enc_id, family_name.get_lang_code_platform_code(cmap.platform_id))
            
                for exact_name in font.exact_names:
                    generated_font["name"].setName(exact_name.value, NameID.FULL_NAME, cmap.platform_id, cmap.platform_enc_id, exact_name.get_lang_code_platform_code(cmap.platform_id))
                    generated_font["name"].setName(exact_name.value, NameID.POSTSCRIPT_NAME, cmap.platform_id, cmap.platform_enc_id, exact_name.get_lang_code_platform_code(cmap.platform_id))
                    generated_font["name"].setName(exact_name.value, NameID.SUBFAMILY_NAME, cmap.platform_id, cmap.platform_enc_id, exact_name.get_lang_code_platform_code(cmap.platform_id))

                    generated_font["name"].setName(
                        f"FontCollector v {__version__}:{exact_name.value}:{date.today()}",
                        NameID.UNIQUE_ID,
                        cmap.platform_id, 
                        cmap.platform_enc_id,
                        exact_name.get_lang_code_platform_code(cmap.platform_id),
                    )

            selection = generated_font["OS/2"].fsSelection
            # First clear...
            selection &= ~(1 << 0)
            selection &= ~(1 << 5)
            selection &= ~(1 << 6)
            # ...then re-set the bits.
            if font.named_instance_coordinates.get("wght", 0) == 400.0:
                selection |= 1 << 6
            if font.named_instance_coordinates.get("ital", 0) == 1:
                selection |= 1 << 0
            if font.named_instance_coordinates.get("wght", 0) > 400.0:
                selection |= 1 << 5
            generated_font["OS/2"].fsSelection = selection

            font_collection.fonts.append(generated_font)

        font_collection.save(save_path)

        if cache_generated_font:
            generated_font = FactoryABCFont.from_font_path(save_path)
            for font in generated_font:
                FontLoader.add_generated_font(font)


    @staticmethod
    def copy_font_to_directory(
        fonts: Iterable[ABCFont],
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

            if isinstance(font, VariableFont):
                font_name = font.get_family_prefix_from_lang("en")
                if len(font_name) == 0:
                    # Get an random families_prefix
                    font_name = list(font.families_prefix)[0].value
                else:
                    font_name = font_name[0].value
            elif isinstance(font, Font):
                font_name = font.get_exact_name_from_lang("en")
                if len(font_name) == 0:
                    # Get an random family_names
                    font_name = list(font.family_names)[0].value
                else:
                    font_name = font_name[0].value
            else:
                raise NotImplementedError(f"The font type {type(font)} hasn't been implemented. Open an issue on Github.")


            if isinstance(font, VariableFont) and convert_variable_font_into_truetype_collection:
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