import logging
import shutil
from pathlib import Path
from sys import argv
from tempfile import TemporaryDirectory

from . import _handler
from .ass.ass_document import AssDocument
from .collect_fonts import collect_subtitle_fonts
from .font import (
    FontCollection,
    FontFile,
    FontLoader,
    FontSelectionStrategyLibass
)
from .mkvtoolnix import MKVExtract, MKVFontFile, MKVPropedit
from .parse_arguments import parse_arguments

_logger = logging.getLogger(__name__)


def main() -> None:
    (
        ass_files_path,
        output_directory,
        mkv_path,
        use_ass_in_mkv,
        delete_fonts,
        additional_fonts_path,
        additional_fonts_recursive_path,
        use_system_font,
        collect_draw_fonts,
        convert_variable_to_collection,
        logging_file_path,
        use_fonts_muxed_to_mkv
    ) = parse_arguments()

    if logging_file_path:
        file_handler = logging.FileHandler(logging_file_path, mode="a", encoding="utf-8")
        file_handler.setLevel(_handler.level)
        file_handler.setFormatter(_handler.formatter)
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
        _logger.info(f"{Path.cwd()}>{' '.join(argv)}")

    try:
        fonts_file_found: set[FontFile] = set()
        additional_fonts = FontLoader.load_additional_fonts(additional_fonts_path)
        additional_fonts.extend(FontLoader.load_additional_fonts(additional_fonts_recursive_path, True))
        if use_fonts_muxed_to_mkv:
            assert mkv_path is not None # Make mypy happy
            tmp_dir_mkv = TemporaryDirectory()
            mkv_font_files = MKVExtract.get_mkv_font_files(mkv_path, Path(tmp_dir_mkv.name))
            additional_fonts.extend(FontLoader.load_additional_fonts([f.filename for f in mkv_font_files]))

        font_collection = FontCollection(use_system_font=use_system_font, additional_fonts=additional_fonts)
        font_strategy = FontSelectionStrategyLibass()

        for ass_path in ass_files_path:
            subtitle = AssDocument.from_file(ass_path)
            _logger.info(f"Loaded successfully {ass_path}")

            fonts_file_found.update(collect_subtitle_fonts(subtitle, font_collection, font_strategy, collect_draw_fonts, True, convert_variable_to_collection, output_directory))
            _logger.info("")

        if use_ass_in_mkv:
            with TemporaryDirectory() as tmp_dir:
                assert isinstance(mkv_path, Path)
                mkv_ass_files = MKVExtract.get_mkv_ass_files(mkv_path, Path(tmp_dir))
                for mkv_ass_file in mkv_ass_files:
                    subtitle = AssDocument.from_file(mkv_ass_file.filename)
                    log_msg = f"Loaded successfully the .ass stream at index {mkv_ass_file.mkv_id}"
                    if mkv_ass_file.track_name:
                        log_msg += f" - \"{mkv_ass_file.track_name}\""
                    _logger.info(log_msg)

                    fonts_file_found.update(collect_subtitle_fonts(subtitle, font_collection, font_strategy, collect_draw_fonts, True, convert_variable_to_collection, output_directory))
                    _logger.info("")

        if mkv_path is not None:
            if delete_fonts:
                MKVPropedit.delete_all_fonts_of_mkv(mkv_path)

            fonts_file_to_mux: set[FontFile] = set()
            if use_fonts_muxed_to_mkv:
                for font in fonts_file_found:
                    if not any(font.filename.samefile(mkv_font.filename) for mkv_font in mkv_font_files):
                        fonts_file_to_mux.add(font)

                mkv_fonts_file_to_delete: list[MKVFontFile] = []
                for mkv_font in mkv_font_files:
                    if not any(mkv_font.filename.samefile(font.filename) for font in fonts_file_found):
                        mkv_fonts_file_to_delete.append(mkv_font)
                if len(mkv_fonts_file_to_delete) > 0:
                    MKVPropedit.delete_fonts_of_mkv(mkv_path, [f.mkv_id for f in mkv_fonts_file_to_delete])

            if len(fonts_file_to_mux) > 0:
                MKVPropedit.merge_fonts_into_mkv(fonts_file_to_mux, mkv_path)
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
    finally:
        if tmp_dir_mkv is not None:
            tmp_dir_mkv.cleanup()

if __name__ == "__main__":
    main()
