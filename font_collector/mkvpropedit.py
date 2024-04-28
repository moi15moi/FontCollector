import logging
import subprocess
from .font.font_file import FontFile
from enum import IntEnum
from pathlib import Path
from shutil import which
from typing import Iterable, Optional

__all__ = ["Mkvpropedit"]
_logger = logging.getLogger(__name__)


class MkvpropeditExitCode(IntEnum):
    # From https://mkvtoolnix.download/doc/mkvpropedit.html#d4e1266
    SUCCESS = 0
    WARNING = 1
    ERROR = 2


class Mkvpropedit:
    """
    This class is a collection of static methods that will help
    the user to interact with mkvpropedit.
    """

    path: Optional[str] = which("mkvpropedit")

    @staticmethod
    def is_mkv(filename: Path) -> bool:
        """
        Args:
            filename: The file name.
        Returns:
            True if the mkv is an mkv file, false in any others cases
        """

        if not filename.is_file():
            raise FileNotFoundError(f'The file "{filename.resolve()}" does not exist.')

        with open(filename, "rb") as f:
            # From https://en.wikipedia.org/wiki/List_of_file_signatures
            return f.read(4) == b"\x1a\x45\xdf\xa3"


    @staticmethod
    def delete_fonts_of_mkv(mkv_filename: Path) -> None:
        """Delete all mkv attached font

        Args:
            mkv_filename: Path to mkv file.
        """

        if Mkvpropedit.path is None:
            raise FileNotFoundError(
                f'"{Mkvpropedit.path}" is not an valid path for Mkvpropedit. You need to correct your environnements variable or change the value of Mkvpropedit.path'
            )

        if not Mkvpropedit.is_mkv(mkv_filename):
            raise FileExistsError(f'The file "{mkv_filename}" is not an mkv file.')

        # We only want to remove ttf, ttc or otf file
        # This is from mpv: https://github.com/mpv-player/mpv/blob/305332f8a06e174c5c45c9c4547293502ac7ecdb/sub/sd_ass.c#L101

        mkvpropedit_args = [
            Mkvpropedit.path,
            str(mkv_filename.resolve()),
            "--delete-attachment", "mime-type:application/x-truetype-font",
            "--delete-attachment", "mime-type:application/vnd.ms-opentype",
            "--delete-attachment", "mime-type:application/x-font-ttf",
            "--delete-attachment", "mime-type:application/x-font",
            "--delete-attachment", "mime-type:application/font-sfnt",
            "--delete-attachment", "mime-type:font/collection",
            "--delete-attachment", "mime-type:font/otf",
            "--delete-attachment", "mime-type:font/sfnt",
            "--delete-attachment", "mime-type:font/ttf",
            "--command-line-charset", "UTF-8",
            "--output-charset", "UTF-8",
        ]

        output = subprocess.run(mkvpropedit_args, capture_output=True, text=True, encoding="utf-8")
        exit_code = MkvpropeditExitCode(output.returncode)

        if exit_code == MkvpropeditExitCode.ERROR:
            raise OSError(
                f"mkvpropedit reported an error when deleting the font in the mkv: {output.stdout}."
            )
        elif exit_code == MkvpropeditExitCode.WARNING:
            _logger.warning(f"mkvpropedit reported an warning when deleting the font in the mkv '{output.stdout}'.")
        elif exit_code == MkvpropeditExitCode.SUCCESS:
            _logger.info(f'Successfully deleted fonts in mkv "{mkv_filename}.')


    @staticmethod
    def merge_fonts_into_mkv(
        fonts_file: Iterable[FontFile],
        mkv_filename: Path,
    ) -> None:
        """Merge font file into the mkv.

        Args:
            fonts_file: All font file that will be merge to the mkv
            mkv_filename: Path to mkv file.
        """
        if Mkvpropedit.path is None:
            raise FileNotFoundError(
                f'"{Mkvpropedit.path}" is not an valid path for Mkvpropedit. You need to correct your environnements variable or change the value of Mkvpropedit.path'
            )

        if not Mkvpropedit.is_mkv(mkv_filename):
            raise FileExistsError(f'The file "{mkv_filename}" is not an mkv file.')

        mkvpropedit_args = [
            Mkvpropedit.path,
            str(mkv_filename.resolve()),
            "--command-line-charset", "UTF-8",
            "--output-charset", "UTF-8",
        ]

        for font_file in fonts_file:
            mkvpropedit_args.extend(['--add-attachment', str(font_file.filename.resolve())])

        output = subprocess.run(mkvpropedit_args, capture_output=True, text=True, encoding="utf-8")
        exit_code = MkvpropeditExitCode(output.returncode)

        if exit_code == MkvpropeditExitCode.ERROR:
            raise OSError(
                f"mkvpropedit reported an error when merging font into an mkv: {output.stdout}"
            )
        elif exit_code == MkvpropeditExitCode.WARNING:
            _logger.warning(f'mkvpropedit reported an warning when merging font into an mkv "{mkv_filename}"')
        elif exit_code == MkvpropeditExitCode.SUCCESS:
            _logger.info(f'Successfully merged fonts into mkv "{mkv_filename}"')
