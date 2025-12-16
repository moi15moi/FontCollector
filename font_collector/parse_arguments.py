from argparse import ArgumentParser
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path

from .mkvtoolnix.mkv_utils import MKVUtils


def __parse_input_file(ass_input: list[Path] | None) -> list[Path]:
    if ass_input is None:
        return []

    ass_files_path = []
    for input in ass_input:
        if input.is_file():
            if input.suffix.lower() == ".ass":
                ass_files_path.append(input)
            else:
                raise FileExistsError("Error: The input file is not an .ass file.")
        elif input.is_dir():
            for file in input.iterdir():
                if file.suffix.lower() == ".ass":
                    ass_files_path.append(file)
        else:
            raise FileNotFoundError(
                f"Error: The input file/folder {input.name} does not exist."
            )

    return ass_files_path


def parse_arguments() -> tuple[
    list[Path],
    Path,
    Path | None,
    bool,
    bool,
    Iterable[Path],
    Iterable[Path],
    bool,
    bool,
    bool,
    Path | None
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
        "--use-ass-in-mkv",
        "-ass-mkv",
        action="store_true",
        help="""
    If specified, it will use the .ass file muxed to the mkv and collect those fonts and mux them to the mkv. If not specified, it will do nothing.
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
        "-mkvtoolnix",
        type=Path,
        help="""
    Path to the MKVToolNix folder if not in variable environments. If -mkv is not specified, it will do nothing.
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
    output_directory = args.output
    mkv_path = args.mkv
    use_ass_in_mkv = args.use_ass_in_mkv
    delete_fonts = args.delete_fonts
    additional_fonts = args.additional_fonts
    additional_fonts_recursive = args.additional_fonts_recursive
    use_system_fonts = args.exclude_system_fonts
    collect_draw_fonts = args.collect_draw_fonts
    convert_variable_to_collection = args.dont_convert_variable_to_collection
    logging_file_path = args.logging

    if len(ass_files_path) == 0 and not use_ass_in_mkv:
        raise RuntimeError("The specified file(s)/folder(s) doesn't exist or the folder(s) doesn't contains any .ass file.")
    
    if use_ass_in_mkv and mkv_path is None:
        raise RuntimeError("You need to add the flag `-mkv` to use the flag `--use-ass-in-mkv`.")

    if args.mkvtoolnix:
        if not mkv_path:
            raise RuntimeError("-mkvtoolnix requires --mkv option.")
        MKVUtils.MKVTOOLNIX_FOLDER = args.mkvtoolnix

    return (
        ass_files_path,
        output_directory,
        mkv_path,
        use_ass_in_mkv,
        delete_fonts,
        additional_fonts,
        additional_fonts_recursive,
        use_system_fonts,
        collect_draw_fonts,
        convert_variable_to_collection,
        logging_file_path
    )
