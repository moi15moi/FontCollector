import logging
import sys
from font_collector import (
    AssDocument,
    Font,
    FontLoader,
    Helpers,
    Mkvpropedit,
    set_loglevel,
)
from pathlib import Path
from typing import List

# If you don't want to get any log, set the loglevel to logging.CRITICAL
set_loglevel(logging.CRITICAL)


def main():
    ass_path = "ASS_FILE_PATH.ass"
    mkv_path = "MKV_FILE_PATH.ass"

    # If you need additional fonts (font that aren't installed in the system), specify them in the additional_fonts_path
    additional_fonts_path: List[Path] = []
    font_collection = FontLoader(additional_fonts_path, use_system_font=True).fonts

    subtitle = AssDocument.from_file(ass_path)
    styles = subtitle.get_used_style()

    fonts_found: List[Font] = []

    for style, usage_data in styles.items():

        font_result = Helpers.get_used_font_by_style(font_collection, style)

        if font_result is None:
            print(f"Could not find font '{style.fontname}'")
        else:
            print(f"Font found: {font_result.font.filename}")
            fonts_found.append(font_result.font)

            # If you wanna verify if the font miss any glyph, use this
            missing_glyphs = font_result.font.get_missing_glyphs(
                usage_data.characters_used
            )
            if len(missing_glyphs) != 0:
                print(
                    f"'{style.fontname}' is missing the following glyphs: {missing_glyphs}"
                )

    # If the mkv already contain font, you can remove them
    Mkvpropedit.delete_fonts_of_mkv(mkv_path)

    Mkvpropedit.merge_fonts_into_mkv(fonts_found, mkv_path)


if __name__ == "__main__":
    sys.exit(main())
