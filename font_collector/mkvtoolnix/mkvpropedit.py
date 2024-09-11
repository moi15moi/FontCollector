import logging
from ..font.font_file import FontFile
from .utils import MKVUtils
from pathlib import Path
from typing import Iterable

__all__ = ["MKVPropedit"]


class MKVPropedit:
    """
    This class is a collection of static methods that will help
    the user to interact with mkvpropedit.
    """

    PROGRAM_NAME = "mkvpropedit"
    PROGRAM_PATH = MKVUtils.get_program_path(PROGRAM_NAME)


    @staticmethod
    def is_mkvpropedit_installed() -> bool:
        """
        Checks if the `mkvmerge` program is installed and available in the system's PATH.

        Returns:
            True if `mkvpropedit` is installed, False otherwise.
        """
        return MKVPropedit.PROGRAM_PATH is not None


    @staticmethod
    def verify_if_mkvpropedit_installed() -> None:
        """
        Verifies if the `mkvpropedit` program is installed. Raises an error if not found.

        Raises:
            Exception: If `mkvpropedit` is not found in the system's PATH.
        """
        if not MKVPropedit.is_mkvpropedit_installed():
            raise Exception(f'{MKVPropedit.PROGRAM_NAME} is isn\'t found. You need to correct your environnements variable or correctly install the program')


    @staticmethod
    def delete_fonts_of_mkv(mkv_filename: Path) -> None:
        """Delete all mkv attached font

        Args:
            mkv_filename: Path to mkv file.
        """

        MKVPropedit.verify_if_mkvpropedit_installed()
        MKVUtils.verify_if_file_mkv(mkv_filename)

        cmd = [
            MKVPropedit.PROGRAM_PATH,
            str(mkv_filename.resolve()),
        ]

        for mime_type in MKVUtils.FONT_MIME_TYPE:
            cmd.extend(['--delete-attachment', f"mime-type:{mime_type}"])

        MKVUtils.run_command(MKVPropedit.PROGRAM_NAME, cmd)


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
        MKVPropedit.verify_if_mkvpropedit_installed()
        MKVUtils.verify_if_file_mkv(mkv_filename)

        cmd = [
            MKVPropedit.PROGRAM_PATH,
            str(mkv_filename.resolve()),
        ]

        for font_file in fonts_file:
            cmd.extend(['--add-attachment', str(font_file.filename.resolve())])

        MKVUtils.run_command(MKVPropedit.PROGRAM_NAME, cmd)