from collections.abc import Iterable
from pathlib import Path
from typing import Optional

from ..font.font_file import FontFile
from .mkv_utils import MKVUtils
from .mkvmerge import MKVMerge

__all__ = ["MKVPropedit"]


class MKVPropedit:
    """
    This class is a collection of static methods that will help
    the user to interact with mkvpropedit.
    """

    PROGRAM_NAME = "mkvpropedit"

    @staticmethod
    def get_program_path() -> Optional[Path]:
        """
        Retrieves the full path to the `mkvpropedit` executable.

        Returns:
            If found, the path to `mkvpropedit`. Otherwise, None.
        """
        return MKVUtils.get_program_path(MKVPropedit.PROGRAM_NAME)


    @staticmethod
    def is_mkvpropedit_installed() -> bool:
        """
        Checks if the `mkvmerge` program is installed and available in the system's PATH.

        Returns:
            True if `mkvpropedit` is installed, False otherwise.
        """
        return MKVPropedit.get_program_path() is not None


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
    def delete_all_fonts_of_mkv(mkv_filename: Path) -> None:
        """Delete all mkv attached font

        Args:
            mkv_filename (Path): Path to mkv file.
        """
        fonts_attachment = MKVMerge.get_mkv_fonts_attachment(mkv_filename)
        if len(fonts_attachment) > 0:
            MKVPropedit.delete_fonts_of_mkv(mkv_filename, [attachment["id"] for attachment in fonts_attachment])


    @staticmethod
    def delete_fonts_of_mkv(mkv_filename: Path, mkv_fonts_id: list[int]) -> None:
        """Delete specified mkv attached font

        Args:
            mkv_filename (Path): Path to mkv file.
            mkv_fonts_id (list[int]): Font(s) id to delete.
        """
        if len(mkv_fonts_id) == 0:
            raise ValueError("You must provide at least 1 font id.")

        MKVPropedit.verify_if_mkvpropedit_installed()
        MKVUtils.verify_if_file_mkv(mkv_filename)

        cmd = [
            MKVPropedit.get_program_path(),
            str(mkv_filename.resolve()),
        ]

        for mkv_font_id in mkv_fonts_id:
            cmd.extend(['--delete-attachment', f"{mkv_font_id}"])

        MKVUtils.run_command(MKVPropedit.PROGRAM_NAME, cmd)


    @staticmethod
    def merge_fonts_into_mkv(
        fonts_file: Iterable[FontFile],
        mkv_filename: Path,
    ) -> None:
        """Merge font file into the mkv.

        Args:
            fonts_file (Iterable[FontFile]): All font file that will be merge to the mkv
            mkv_filename (Path): Path to mkv file.
        """
        MKVPropedit.verify_if_mkvpropedit_installed()
        MKVUtils.verify_if_file_mkv(mkv_filename)

        cmd = [
            MKVPropedit.get_program_path(),
            str(mkv_filename.resolve()),
        ]

        for font_file in fonts_file:
            cmd.extend(['--add-attachment', str(font_file.filename.resolve())])

        MKVUtils.run_command(MKVPropedit.PROGRAM_NAME, cmd)
