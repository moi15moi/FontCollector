import logging
import shutil
from pathlib import Path
from sys import argv

from . import _handler
from .ass.ass_document import AssDocument
from .font import (
    FontCollection,
    FontFile,
    FontLoader,
    FontSelectionStrategyLibass,
    VariableFontFace,
    font_weight_to_name
)
from .mkvpropedit import Mkvpropedit
from .parse_arguments import parse_arguments

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
        convert_variable_to_collection,
        logging_file_path
    ) = parse_arguments()

    if logging_file_path:
        file_handler = logging.FileHandler(logging_file_path, mode="a", encoding="utf-8")
        file_handler.setLevel(_handler.level)
        file_handler.setFormatter(_handler.formatter)
        _logger.addHandler(file_handler)
        _logger.info(f"{Path.cwd()}>{' '.join(argv)}")

    try:
        fonts_file_found: set[FontFile] = set()
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
                    _logger.error(
                        f"Could not find font '{style.fontname}'\n"
                        f"Used on lines: {' '.join(str(line) for line in usage_data.ordered_lines)}"
                    )
                else:
                    log_msg = ""
                    if font_result.need_faux_bold:
                        log_msg = f"Faux bold used for '{style.fontname}' (requested weight {style.weight}-{(font_weight_to_name(style.weight))}, got {font_result.font_face.weight}-{(font_weight_to_name(font_result.font_face.weight))})."
                    elif font_result.mismatch_bold:
                        log_msg = f"Mismatched weight for '{style.fontname}' (requested weight {style.weight}-{(font_weight_to_name(style.weight))}, got {font_result.font_face.weight}-{(font_weight_to_name(font_result.font_face.weight))})."
                    if font_result.mismatch_italic:
                        log_msg = f"Mismatched italic for '{style.fontname}' (requested {'' if style.italic else 'non-'}italic, got {'' if font_result.font_face.is_italic else 'non-'}italic)."

                    if log_msg:
                        _logger.warning(
                            f"{log_msg}\n"
                            f"Used on lines: {' '.join(str(line) for line in usage_data.ordered_lines)}"
                        )


                    missing_glyphs = font_result.font_face.get_missing_glyphs(usage_data.characters_used)
                    if len(missing_glyphs) > 0:
                        _logger.warning(f"'{style.fontname}' is missing the following glyphs used: {missing_glyphs}")


                    if font_result.font_face.font_file is None:
                        raise ValueError(f"This font_face \"{font_result.font_face}\" isn't linked to any FontFile.")

                    if convert_variable_to_collection and isinstance(font_result.font_face, VariableFontFace):
                        font_name = font_result.font_face.get_best_family_prefix_from_lang().value
                        font_filename = output_directory.joinpath(f"{font_name}.ttc")
                        generated_font_file = font_result.font_face.variable_font_to_collection(font_filename)
                        fonts_file_found.add(generated_font_file)
                    else:
                        fonts_file_found.add(font_result.font_face.font_file)

            if nbr_font_not_found == 0:
                _logger.info(f"All font(s) found")
            else:
                _logger.error(f"{nbr_font_not_found} font(s) could not be found.")

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
    except Exception as e:
        _logger.error("An unexpected error occured", exc_info=True)

if __name__ == "__main__":
    main()
