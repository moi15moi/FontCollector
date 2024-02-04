import logging
import sys
from font_collector import (
    AssDocument,
    Font,
    FontLoader,
    FontCollection,
    Helpers,
    Mkvpropedit,
    set_loglevel,
)
from pathlib import Path
from typing import List

# If you don't want to get any log, set the loglevel to logging.CRITICAL
set_loglevel(logging.CRITICAL)


def main():
    ass_path = r"C:\Users\Admin\Desktop\Untitled.ass"
    mkv_path = "MKV_FILE_PATH.ass"

    FontLoader.discard_system_font_cache()
    FontLoader.discard_generated_font_cache()

    # If you need additional fonts (font that aren't installed in the system), specify them in the additional_fonts_path
    additional_fonts_path: List[Path] = []
    font_collection = FontCollection()


    for font in font_collection:
        families = font.get_exact_name_from_lang("en")
        if len(families) > 0 and families[0].value == "Arial":
            print(font.filename)


    # If the mkv already contain font, you can remove them
    #Mkvpropedit.delete_fonts_of_mkv(mkv_path)

    #Mkvpropedit.merge_fonts_into_mkv(fonts_found, mkv_path)


if __name__ == "__main__":
    sys.exit(main())
