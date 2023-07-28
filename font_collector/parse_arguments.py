import os
from .font import Font
from .font_loader import FontLoader
from .mkvpropedit import Mkvpropedit
from argparse import ArgumentParser
from pathlib import Path
from typing import List, Set, Tuple, Union


def _parse_input_file(ass_input: List[Path]) -> List[Path]:

    if len(ass_input) == 0:
        return [Path(file) for file in os.listdir(os.getcwd()) if file.endswith(".ass")]

    ass_files_path = []
    for input in ass_input:
        if os.path.isfile(input):
            if input.name.endswith(".ass"):
                ass_files_path.append(Path(input))
            else:
                raise FileExistsError("Error: The input file is not an .ass file.")
        elif os.path.isdir(input):
            for file in os.listdir(input):
                if file.endswith(".ass"):
                    ass_files_path.append(Path(os.path.join(input, file)))
        else:
            raise FileNotFoundError(
                f"Error: The input file/folder {input.name} does not exist."
            )

    return ass_files_path


def parse_arguments() -> Tuple[
    List[Path],
    Path,
    Union[Path, None],
    bool,
    Set[Path],
    bool,
    bool
]:
    """
    Returns:
        ass_files_path, output_directory, mkv_path, delete_fonts, additional_fonts, use_system_fonts
    """
    parser = ArgumentParser(
        description="FontCollector for Advanced SubStation Alpha file."
    )
    parser.add_argument(
        "--input",
        "-i",
        nargs="*",
        type=Path,
        required=True,
        help="""
    Subtitles file. Must be an ASS file/directory. You can specify more than one .ass file/path. If no argument is specified, it will take all the font in the current path.
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
        default=os.getcwd(),
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
        nargs="+",
        type=Path,
        help="""
    May be a directory containing font files or a single font file. You can specify more than one additional-fonts.
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

    args = parser.parse_args()

    # Parse args
    ass_files_path = _parse_input_file(args.input)

    output_directory = args.output

    mkv_path = args.mkv
    if mkv_path:
        if args.mkvpropedit is not None:
            Mkvpropedit.path = args.mkvpropedit

    delete_fonts = args.delete_fonts

    if args.additional_fonts is not None:
        additional_fonts = args.additional_fonts
    else:
        additional_fonts = set()

    use_system_fonts = args.exclude_system_fonts
    collect_draw_fonts = args.collect_draw_fonts

    return (
        ass_files_path,
        output_directory,
        mkv_path,
        delete_fonts,
        additional_fonts,
        use_system_fonts,
        collect_draw_fonts
    )
