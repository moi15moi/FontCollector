import logging
import sys
from typing import List
from .parse_arguments import parse_arguments

from .ass_document import AssDocument
from .font_loader import FontLoader
from .font_result import FontResult
from .helpers import Helpers
from .mkvpropedit import Mkvpropedit

_logger = logging.getLogger(__name__)

def main():
    ass_files_path, output_directory, mkv_path, delete_fonts, additional_fonts, use_system_font = parse_arguments()
    font_results: List[FontResult] = []

    for ass_path in ass_files_path:
        subtitle = AssDocument.from_file(ass_path)
        _logger.info(f"Loaded successfully {ass_path}")
        styles = subtitle.get_used_style()

        font_collection = FontLoader(additional_fonts, use_system_font).fonts

        for style, usage_data in styles.items():

            font_result = Helpers.get_used_font_by_style(font_collection, style)

            # Did not found the font
            if font_result is None:
                _logger.error(f"Used on lines: {' '.join(str(line) for line in usage_data.ordered_lines)}")
            else:
                font_results.append(font_result)

                if font_result.mismatch_bold:
                    _logger.warning(f"'{style.fontname}' does not have a bold variant.")
                if font_result.mismatch_italic:
                    _logger.warning(f"'{style.fontname}' does not have an italic variant.")
                
                if font_result.mismatch_bold or font_result.mismatch_italic:
                    _logger.warning(f"Used on lines: {' '.join(str(line) for line in usage_data.ordered_lines)}")

                if (
                    len(
                        missing_glyphs := font_result.font.get_missing_glyphs(
                            usage_data.characters_used
                        )
                    )
                    > 0
                ):                
                    _logger.warning(f"'{style.fontname}' is missing the following glyphs used: {missing_glyphs}")

    
    font_found = list({ font.font.filename : font.font for font in font_results}.values())
    if mkv_path is not None:
        if delete_fonts:
            Mkvpropedit.delete_fonts_of_mkv(mkv_path)
        Mkvpropedit.merge_fonts_into_mkv(font_found, mkv_path)
    else:
        Helpers.copy_font_to_directory(font_found, output_directory)



if __name__ == "__main__":
    sys.exit(main())
