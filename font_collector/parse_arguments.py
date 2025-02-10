from argparse import ArgumentParser
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

from .mkvpropedit import Mkvpropedit


def __parse_input_file(ass_input: list[Path]) -> list[Path]:

    ass_files_path = []
    for input in ass_input:
        if input.is_file():
            if input.suffix.casefold() == ".ass":
                ass_files_path.append(input)
            else:
                raise FileExistsError("Error: The input file is not an .ass file.")
        elif input.is_dir():
            for file in input.iterdir():
                if file.suffix.casefold() == ".ass":
                    ass_files_path.append(file)
        else:
            raise FileNotFoundError(
                f"Error: The input file/folder {input.name} does not exist."
            )

    return ass_files_path


def parse_arguments() -> tuple[
    list[Path],
    Path,
    Union[Path, None],
    bool,
    Iterable[Path],
    Iterable[Path],
    bool,
    bool,
    bool,
    Optional[Path]
]:
    """
    Returns:
        ass_files_path, output_directory, mkv_path, delete_fonts, additional_fonts, use_system_fonts
    """

    start_time = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
    default_log_path = Path.cwd().joinpath(f"{start_time}_font_collector.log")

    parser = ArgumentParser(
        description="FontCollector for Advanced SubStation Alpha file."
    )
    parser.add_argument(
        "--input",
        "-i",
        nargs="+",
        type=Path,
        required=True,
        help="""
    Subtitles file. Must be an ASS file/directory. You can specify more than one .ass file/path.
    """,
    )
    parser.add_argument(
        "-mkv",
        type=Path,
        help="""
    Video where the fonts will be merge. Must be a Matroska file.
    """,
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path.cwd(),
        help="""
    Destination path of the font. If -o and -mkv aren't specified, it will be the current path.
    """,
    )
    parser.add_argument(
        "-mkvpropedit",
        type=Path,
        help="""
    Path to mkvpropedit.exe if not in variable environments. If -mkv is not specified, it will do nothing.
    """,
    )
    parser.add_argument(
        "--delete-fonts",
        "-d",
        action="store_true",
        help="""
    If -d is specified, it will delete the font attached to the mkv before merging the new needed font. If -mkv is not specified, it will do nothing.
    """,
    )
    parser.add_argument(
        "--additional-fonts",
        "-add-fonts",
        nargs="+",
        default=set(),
        type=Path,
        help="""
    May be a directory containing font files or a single font file. You can specify more than one additional-fonts.
    If it is a directory, it won't search recursively for fonts
    """,
    )
    parser.add_argument(
        "--additional-fonts-recursive",
        "-add-fonts-rec",
        nargs="+",
        default=set(),
        type=Path,
        help="""
    Path to font directory, which will be recursively searched for fonts.
    """,
    )
    parser.add_argument(
        "--exclude-system-fonts",
        action="store_false",
        help="""
    If specified, FontCollector won't use the system font to find the font used by an .ass file.
    """,
    )
    parser.add_argument(
        "--collect-draw-fonts",
        action="store_true",
        help="""
    If specified, FontCollector will collect the font used by the draw. For more detail when this is usefull, see: https://github.com/libass/libass/issues/617
    """,
    )
    parser.add_argument(
        "--dont-convert-variable-to-collection",
        action="store_false",
        help="""
    If specified, FontCollector won't convert variable font to a font collection. see: https://github.com/libass/libass/issues/386
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
    Destination path of log. If it isn't specified, it will be YYYY-MM-DD--HH-MM-SS_font_collector.log.
    """,
    )

    args = parser.parse_args()

    # Parse args
    ass_files_path = __parse_input_file(args.input)

    if len(ass_files_path) == 0:
        raise RuntimeError("The specified file(s)/folder(s) doesn't exist or the folder(s) doesn't contains any .ass file.")

    output_directory = args.output
    mkv_path = args.mkv
    delete_fonts = args.delete_fonts
    additional_fonts = args.additional_fonts
    additional_fonts_recursive = args.additional_fonts_recursive
    use_system_fonts = args.exclude_system_fonts
    collect_draw_fonts = args.collect_draw_fonts
    convert_variable_to_collection = args.dont_convert_variable_to_collection
    logging_file_path = args.logging

    if args.mkvpropedit:
        if not mkv_path:
            raise RuntimeError("-mkvpropedit requires --mkv option.")
        Mkvpropedit.path = args.mkvpropedit

    return (
        ass_files_path,
        output_directory,
        mkv_path,
        delete_fonts,
        additional_fonts,
        additional_fonts_recursive,
        use_system_fonts,
        collect_draw_fonts,
        convert_variable_to_collection,
        logging_file_path
    )
