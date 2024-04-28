import logging
import shutil
from .ass.ass_document import AssDocument
from .font import FontCollection, FontFile, FontLoader, FontResult, FontSelectionStrategyLibass, VariableFontFace
from .mkvpropedit import Mkvpropedit
from .parse_arguments import parse_arguments
from pathlib import Path
from typing import List, Set


_logger = logging.getLogger(__name__)


def main() -> None:
    (
        ass_files_path,
        output_directory,
        mkv_path,
        delete_fonts,
        additional_fonts_path,
        additional_fonts_recursive_path,
        use_system_font,
        collect_draw_fonts,
        convert_variable_to_collection
    ) = parse_arguments()
    font_results: List[FontResult] = []
    additional_fonts = FontLoader.load_additional_fonts(additional_fonts_path)
    additional_fonts.extend(FontLoader.load_additional_fonts(additional_fonts_recursive_path, True))
    font_collection = FontCollection(use_system_font=use_system_font, additional_fonts=additional_fonts)
    font_strategy = FontSelectionStrategyLibass()

    for ass_path in ass_files_path:
        subtitle = AssDocument.from_file(ass_path)
        _logger.info(f"Loaded successfully {ass_path}")
        used_styles = subtitle.get_used_style(collect_draw_fonts)

        nbr_font_not_found = 0

        for style, usage_data in used_styles.items():

            font_result = font_collection.get_used_font_by_style(style, font_strategy)

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

    fonts_file_found: Set[FontFile] = set()

    for font_result in font_results:
        if font_result.font_face.font_file is None:
            raise ValueError(f"This font_face \"{font_result.font_face}\" isn't linked to any FontFile.")

        if convert_variable_to_collection and isinstance(font_result.font_face, VariableFontFace):
            font_name = font_result.font_face.get_best_family_prefix_from_lang().value
            font_filename = output_directory.joinpath(f"{font_name}.ttc")
            generated_font_file = font_result.font_face.variable_font_to_collection(font_filename)
            fonts_file_found.add(generated_font_file)
        else:
            fonts_file_found.add(font_result.font_face.font_file)

    if mkv_path is not None:
        if delete_fonts:
            Mkvpropedit.delete_fonts_of_mkv(mkv_path)
        Mkvpropedit.merge_fonts_into_mkv(fonts_file_found, mkv_path)
    else:
        if not output_directory.is_dir():
            output_directory.mkdir()

        for font in fonts_file_found:
                font_filename = output_directory.joinpath(font.filename.resolve().name)
                # Don't overwrite fonts
                if not font_filename.is_file():
                    shutil.copy(font.filename, font_filename)

if __name__ == "__main__":
    main()
