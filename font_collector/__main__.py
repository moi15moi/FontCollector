# TODO Vérifier s'il y a des différences avec ce code, la V3 en ligne ET la v2.1.4




import logging
import os
import shutil
import sys
from .ass.ass_document import AssDocument
from .font import FontCollection, FontFile, FontLoader, FontResult, Helpers, VariableFontFace
from .mkvpropedit import Mkvpropedit
from .parse_arguments import parse_arguments
from typing import List, Set


_logger = logging.getLogger(__name__)


def main():
    (
        ass_files_path,
        output_directory,
        mkv_path,
        delete_fonts,
        additional_fonts,
        additional_fonts_recursive,
        use_system_font,
        collect_draw_fonts,
        convert_variable_to_collection
    ) = parse_arguments()
    font_results: List[FontResult] = []
    additional_fonts = FontLoader.load_additional_fonts(additional_fonts)
    additional_fonts.extend(FontLoader.load_additional_fonts(additional_fonts_recursive, True))
    font_collection = FontCollection(use_system_font=use_system_font, additional_fonts=additional_fonts)

    for ass_path in ass_files_path:
        subtitle = AssDocument.from_file(ass_path)
        _logger.info(f"Loaded successfully {ass_path}")
        used_styles = subtitle.get_used_style(collect_draw_fonts)

        nbr_font_not_found = 0

        for style, usage_data in used_styles.items():

            font_result = font_collection.get_used_font_by_style(style)

            # Did not found the font
            if font_result is None:
                nbr_font_not_found += 1
                _logger.error(f"Could not find font '{style.fontname}'")
                _logger.error(f"Used on lines: {' '.join(str(line) for line in usage_data.ordered_lines)}")
            else:
                font_results.append(font_result)

                if font_result.need_faux_bold:
                    _logger.warning(f"Faux bold used for '{style.fontname}'.")
                elif font_result.mismatch_bold:
                    _logger.warning(f"'{style.fontname}' does not have a bold variant.")
                if font_result.mismatch_italic:
                    _logger.warning(f"'{style.fontname}' does not have an italic variant.")

                if font_result.need_faux_bold or font_result.mismatch_bold or font_result.mismatch_italic:
                    _logger.warning(f"Used on lines: {' '.join(str(line) for line in usage_data.ordered_lines)}")

                
                missing_glyphs = font_result.font_face.get_missing_glyphs(usage_data.characters_used)
                if len(missing_glyphs) > 0:
                    _logger.warning(f"'{style.fontname}' is missing the following glyphs used: {missing_glyphs}")

        if nbr_font_not_found == 0:
            _logger.info(f"All fonts found")
        else:
            _logger.info(f"{nbr_font_not_found} fonts could not be found.")
    
    if convert_variable_to_collection:
        fonts_file_found: Set[FontFile] = set()

        for font_result in font_results:
            if isinstance(font_result.font_face, VariableFontFace):
                font_name = font_result.font_face.get_family_prefix_from_lang("en")
                if len(font_name) == 0:
                    # Get an random families_prefix
                    font_name = list(font_result.font_face.families_prefix)[0].value
                else:
                    font_name = font_name[0].value
                font_filename = os.path.join(output_directory, f"{font_name}.ttc")
                if not any(font.filename == font_filename for font in fonts_file_found):
                    generated_font_file = font_result.font_face.variable_font_to_collection(font_filename)
                    fonts_file_found.add(generated_font_file)
            else:
                fonts_file_found.add(font_result.font_face.font_file)
    else:
        fonts_file_found: Set[FontFile] = {font_result.font_face.font_file for font_result in font_results}

    if mkv_path is not None:
        if delete_fonts:
            Mkvpropedit.delete_fonts_of_mkv(mkv_path)
        Mkvpropedit.merge_fonts_into_mkv(fonts_file_found, mkv_path)
    else:
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        for font in fonts_file_found:
                font_filename = os.path.join(output_directory, os.path.basename(font.filename))                
                # Don't overwrite fonts
                if not os.path.isfile(font_filename):
                    shutil.copy(font.filename, font_filename)

if __name__ == "__main__":
    sys.exit(main())
