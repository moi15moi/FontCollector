import logging
from argparse import ArgumentParser
from datetime import datetime
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
from .mkvtoolnix import MKVExtract, MKVFontFile, MKVPropedit, MKVUtils

_logger = logging.getLogger(__name__)


def main() -> None:
    start_time = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
    default_log_path = Path.cwd().joinpath(f"{start_time}_mkvfontvalidator.log")

    parser = ArgumentParser(
        description="MKV font validator for Advanced SubStation Alpha file."
    )
    parser.add_argument(
        "-mkv",
        type=Path,
        required=True,
        help="""
    The video file to be verified. Must be a Matroska file.
    """,
    )
    parser.add_argument(
        "-mkvtoolnix",
        type=Path,
        help="""
    Path to the MKVToolNix folder if not in variable environments.
    """,
    )
    parser.add_argument(
        "--need-draw-fonts",
        action="store_true",
        help="""
        If specified, MKVFontValidator will report a error if a font used in a draw isn't muxed to the mkv. For more detail when this is usefull, see: https://github.com/libass/libass/issues/617
    """,
    )
    parser.add_argument(
        "--delete-fonts-not-used",
        "-d",
        action="store_true",
        help="""
        If specified, MKVFontValidator will remove the fonts that aren't used by the subtitle(s) of the mkv file.
    """,
    )
    parser.add_argument(
        "--logging",
        "-log",
        type=Path,
        nargs="?",
        const=default_log_path,
        default=None,
        help="""
    Destination path of log. If it isn't specified, it will be YYYY-MM-DD--HH-MM-SS_mkvfontvalidator.log.
    """,
    )

    args = parser.parse_args()

    mkv_path: Path = args.mkv
    need_draw_fonts: bool = args.need_draw_fonts
    delete_fonts_not_used: bool = args.delete_fonts_not_used
    logging_file_path: Path | None = args.logging

    if args.mkvtoolnix:
        MKVUtils.MKVTOOLNIX_FOLDER = args.mkvtoolnix

    if logging_file_path:
        file_handler = logging.FileHandler(logging_file_path, mode="a", encoding="utf-8")
        file_handler.setLevel(_handler.level)
        file_handler.setFormatter(_handler.formatter)
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
        _logger.info(f"{Path.cwd()}>{' '.join(argv)}")

    try:
        with TemporaryDirectory() as tmp_dir:

            mkv_ass_files = MKVExtract.get_mkv_ass_files(mkv_path, Path(tmp_dir))
            mkv_font_files = MKVExtract.get_mkv_font_files(mkv_path, Path(tmp_dir))

            fonts_file_found: set[FontFile] = set()
            additional_fonts = FontLoader.load_additional_fonts([f.filename for f in mkv_font_files])
            font_collection = FontCollection(use_system_font=False, use_generated_fonts=False, additional_fonts=additional_fonts)
            font_strategy = FontSelectionStrategyLibass()

            for mkv_ass_file in mkv_ass_files:
                subtitle = AssDocument.from_file(mkv_ass_file.filename)
                log_msg = f"Loaded successfully the .ass stream at index {mkv_ass_file.mkv_id}"
                if mkv_ass_file.track_name:
                    log_msg += f" - \"{mkv_ass_file.track_name}\""
                _logger.info(log_msg)

                fonts_file_found.update(collect_subtitle_fonts(subtitle, font_collection, font_strategy, need_draw_fonts, False, False, None))
                _logger.info("")

            font_not_used: list[MKVFontFile] = []
            for mkv_font_file in mkv_font_files:
                if not any(mkv_font_file.filename.samefile(font_file.filename) for font_file in fonts_file_found):
                    font_not_used.append(mkv_font_file)

                    if not delete_fonts_not_used:
                        _logger.warning(f"You can remove the font at the id {mkv_font_file.mkv_id} named \"{mkv_font_file.mkv_font_filename}\". It is not used by any .ass file.")

            if delete_fonts_not_used and font_not_used:
                MKVPropedit.delete_fonts_of_mkv(mkv_path, [mkv_font.mkv_id for mkv_font in font_not_used])
                _logger.info(f'Successfully deleted {", ".join([f"{mkv_font.mkv_id}-{mkv_font.mkv_font_filename}" for mkv_font in font_not_used])} of the mkv "{mkv_path}"')
    except Exception as e:
        _logger.error("An unexpected error occured", exc_info=True)


if __name__ == "__main__":
    main()
