from argparse import ArgumentParser
import logging
import shutil
from .ass.ass_document import AssDocument
from .font import FontCollection, FontFile, FontLoader, FontResult, FontSelectionStrategyLibass, VariableFontFace
from .mkvtoolnix import MKVPropedit, MKVExtract
from .parse_arguments import parse_arguments
from pathlib import Path
from typing import List, Set


_logger = logging.getLogger(__name__)


def main() -> None:
    
    parser = ArgumentParser(
        description="MKV font validator for Advanced SubStation Alpha file."
    )
    parser.add_argument(
        "-mkv",
        type=Path,
        help="""
    The video file to be verified. Must be a Matroska file.
    """,
    )
    parser.add_argument(
        "-mkvpropedit",
        type=Path,
        help="""
    Path to mkvpropedit.exe if not in variable environments.
    """,
    )
    parser.add_argument(
        "--need-draw-fonts",
        action="store_true",
        help="""
        If specified, FontCollector will report a error if a font used in a draw isn't muxed to the mkv. For more detail when this is usefull, see: https://github.com/libass/libass/issues/617
    """,
    )

    args = parser.parse_args()

    mkv_path = args.mkv
    need_draw_fonts = args.need_draw_fonts

    if args.mkvpropedit:
        MKVPropedit.path = args.mkvpropedit
    
    mkv_ass_files = MKVExtract.get_mkv_ass_files(mkv_path)
    mkv_font_files = MKVExtract.get_mkv_font_files(mkv_path)

    font_results: List[FontResult] = []
    additional_fonts = FontLoader.load_additional_fonts([f.filename.path for f in mkv_font_files])
    font_collection = FontCollection(use_system_font=False, additional_fonts=additional_fonts)
    font_strategy = FontSelectionStrategyLibass()

    for mkv_ass_file in mkv_ass_files:
        subtitle = AssDocument.from_file(mkv_ass_file.filename.path)
        _logger.info(f"Loaded successfully the .ass stream at index {mkv_ass_file.mkv_id}")
        used_styles = subtitle.get_used_style(need_draw_fonts)

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

    for mkv_font_file in mkv_font_files:
        if not any(mkv_font_file.filename.path.samefile(font_result.font_face.font_file.filename) for font_result in font_results):
            _logger.warning(f"You can remove the font at the id {mkv_font_file.mkv_id}. It is not used by any .ass file.")

if __name__ == "__main__":
    main()
