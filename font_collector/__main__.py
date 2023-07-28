import logging
import sys
from .ass_document import AssDocument
from .font import Font
from .font_loader import FontLoader
from .font_result import FontResult
from .helpers import Helpers
from .mkvpropedit import Mkvpropedit
from .parse_arguments import parse_arguments
from typing import List


_logger = logging.getLogger(__name__)


def main():
    (
        ass_files_path,
        output_directory,
        mkv_path,
        delete_fonts,
        additional_fonts,
        use_system_font,
        collect_draw_fonts
    ) = parse_arguments()
    font_results: List[FontResult] = []
    font_collection = FontLoader(additional_fonts, use_system_font).fonts

    for ass_path in ass_files_path:
        subtitle = AssDocument.from_file(ass_path)
        _logger.info(f"Loaded successfully {ass_path}")
        styles = subtitle.get_used_style(collect_draw_fonts)

        nbr_font_not_found = 0

        for style, usage_data in styles.items():

            font_result = Helpers.get_used_font_by_style(font_collection, style)

            # Did not found the font
            if font_result is None:
                nbr_font_not_found += 1
                _logger.error(
                    f"Used on lines: {' '.join(str(line) for line in usage_data.ordered_lines)}"
                )
            else:
                font_results.append(font_result)

                if font_result.mismatch_bold:
                    _logger.warning(f"'{style.fontname}' does not have a bold variant.")
                if font_result.mismatch_italic:
                    _logger.warning(
                        f"'{style.fontname}' does not have an italic variant."
                    )

                if font_result.mismatch_bold or font_result.mismatch_italic:
                    _logger.warning(
                        f"Used on lines: {' '.join(str(line) for line in usage_data.ordered_lines)}"
                    )

                if (
                    len(
                        missing_glyphs := font_result.font.get_missing_glyphs(
                            usage_data.characters_used
                        )
                    )
                    > 0
                ):
                    _logger.warning(
                        f"'{style.fontname}' is missing the following glyphs used: {missing_glyphs}"
                    )

        if nbr_font_not_found == 0:
            _logger.info(f"All fonts found")
        else:
            _logger.info(f"{nbr_font_not_found} fonts could not be found.")

    fonts_found: List[Font] = [font.font for font in font_results]

    if mkv_path is not None:
        if delete_fonts:
            Mkvpropedit.delete_fonts_of_mkv(mkv_path)
        Mkvpropedit.merge_fonts_into_mkv(fonts_found, mkv_path)
    else:
        Helpers.copy_font_to_directory(fonts_found, output_directory)


if __name__ == "__main__":
    sys.exit(main())
