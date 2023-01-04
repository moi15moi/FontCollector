import shutil
import subprocess
from .font import Font
from os import path
from pathlib import Path
from typing import Sequence


class Mkvpropedit:
    path: str = shutil.which("mkvpropedit")

    @staticmethod
    def is_mkv(filename: Path) -> bool:
        """
        Parameters:
            filename (Path): The file name. Example: "example.mkv"
        Returns:
            True if the mkv is an mkv file, false in any others cases
        Thanks to https://github.com/TypesettingTools/Myaamori-Aegisub-Scripts/blob/f2a52ee38eeb60934175722fa9d7f2c2aae015c6/scripts/fontvalidator/fontvalidator.py#L414
        """

        if not path.exists(filename):
            raise FileNotFoundError(f'The file "{filename}" does not exist.')

        with open(filename, "rb") as f:
            # From https://en.wikipedia.org/wiki/List_of_file_signatures
            return f.read(4) == b"\x1a\x45\xdf\xa3"

    @staticmethod
    def is_mkvpropedit_path_valid() -> bool:

        mkvpropeditOutput = subprocess.run(
            f"{Mkvpropedit.path} --version", capture_output=True, text=True
        )
        return mkvpropeditOutput.stdout.startswith("mkvpropedit")

    @staticmethod
    def delete_fonts_of_mkv(mkv_filename: Path) -> None:
        """
        Delete all mkv attached font
        Parameters:
            mkvFileName (Path): Path to mkvFile
        """

        if not Mkvpropedit.is_mkvpropedit_path_valid():
            raise FileNotFoundError(
                f'"{Mkvpropedit.path}" is not an valid path for Mkvpropedit. You need to correct your environnements variable or change the value of Mkvpropedit.path'
            )

        if not Mkvpropedit.is_mkv(mkv_filename):
            raise FileExistsError(f'The file "{mkv_filename}" is not an mkv file.')

        # We only want to remove ttf, ttc or otf file
        # This is from mpv: https://github.com/mpv-player/mpv/blob/305332f8a06e174c5c45c9c4547293502ac7ecdb/sub/sd_ass.c#L101

        mkvpropedit_args = [
            f'"{Mkvpropedit.path}"',
            f'"{mkv_filename}"',
            "--delete-attachment mime-type:application/x-truetype-font",
            "--delete-attachment mime-type:application/vnd.ms-opentype",
            "--delete-attachment mime-type:application/x-font-ttf",
            "--delete-attachment mime-type:application/x-font",
            "--delete-attachment mime-type:application/font-sfnt",
            "--delete-attachment mime-type:font/collection",
            "--delete-attachment mime-type:font/otf",
            "--delete-attachment mime-type:font/sfnt",
            "--delete-attachment mime-type:font/ttf",
        ]

        output = subprocess.run(
            " ".join(mkvpropedit_args), capture_output=True, text=True
        )

        if len(output.stderr) != 0:
            raise OSError(
                f"mkvpropedit reported an error when deleting the font in the mkv: {output.stderr}"
            )

    @staticmethod
    def merge_fonts_into_mkv(font_collection: Sequence[Font], mkv_filename: Path):
        """
        Parameters:
            font_collection (Sequence[Font]): All font needed to be merge in the mkv
            mkv_filename (Path): Mkv file path
        """
        if not Mkvpropedit.is_mkvpropedit_path_valid():
            raise FileNotFoundError(
                f'"{Mkvpropedit.path}" is not an valid path for Mkvpropedit. You need to correct your environnements variable or change the value of Mkvpropedit.path'
            )

        if not Mkvpropedit.is_mkv(mkv_filename):
            raise FileExistsError(f'The file "{mkv_filename}" is not an mkv file.')

        mkvpropedit_args = [
            f'"{Mkvpropedit.path}"',
            f'"{mkv_filename}"',
        ]

        for font in font_collection:
            mkvpropedit_args.append(f'--add-attachment "{font.filename}"')

        output = subprocess.run(
            " ".join(mkvpropedit_args), capture_output=True, text=True
        )

        if len(output.stderr) != 0:
            raise OSError(
                f"mkvpropedit reported an error when merging font into an mkv: {output.stderr}"
            )
