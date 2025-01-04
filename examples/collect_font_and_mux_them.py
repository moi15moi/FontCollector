import logging
import sys
from font_collector import (
    AssDocument,
    FontCollection,
    FontFile,
    FontLoader,
    FontSelectionStrategyLibass,
    Mkvpropedit,
    set_loglevel,
)
from pathlib import Path
from typing import List, Set

# If you don't want to get any log, set the loglevel to logging.CRITICAL
set_loglevel(logging.CRITICAL)


def main():
    ass_path = Path("ASS_FILE_PATH.ass")
    mkv_path = Path("MKV_FILE_PATH.mkv")

    additional_fonts_path: list[Path] = []
    additional_fonts = FontLoader.load_additional_fonts(additional_fonts_path)

    # If you need additional fonts (font that aren't installed in the system), specify them in the additional_fonts
    font_collection = FontCollection(additional_fonts=additional_fonts)
    font_selection_strategy = FontSelectionStrategyLibass()

    subtitle = AssDocument.from_file(ass_path) # if you have a object that represent the .ass file, you can also use ABCAssDocument
    used_styles = subtitle.get_used_style()

    fonts_file_found: set[FontFile] = set()

    for style, usage_data in used_styles.items():
        font_result = font_collection.get_used_font_by_style(style, font_selection_strategy)
        if font_result:
            family_name = font_result.font_face.get_best_family_name()
            font_file = font_result.font_face.font_file
            print(f"We found the family {family_name.value} at {font_file.filename}")
            fonts_file_found.add(font_file)

            # If you wanna verify if the font miss any glyph, use this
            missing_glyphs = font_result.font_face.get_missing_glyphs(usage_data.characters_used)
            if len(missing_glyphs) != 0:
                print(f"'{family_name.value}' is missing the following glyphs: {missing_glyphs}")


    # If the mkv already contains font, you can remove them
    Mkvpropedit.delete_fonts_of_mkv(mkv_path)

    Mkvpropedit.merge_fonts_into_mkv(fonts_file_found, mkv_path)


if __name__ == "__main__":
    sys.exit(main())
