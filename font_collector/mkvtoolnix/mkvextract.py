from pathlib import Path
from typing import Optional

from .mkv_ass_file import MKVASSFile
from .mkv_font_file import MKVFontFile
from .mkv_utils import MKVUtils
from .mkvmerge import MKVMerge

__all__ = ["MKVExtract"]


class MKVExtract:
    """
    This class is a collection of static methods that will help
    the user to interact with mkvextract.
    """

    PROGRAM_NAME = "mkvextract"

    @staticmethod
    def get_program_path() -> Path | None:
        """
        Retrieves the full path to the `mkvextract` executable.

        Returns:
            If found, the path to `mkvextract`. Otherwise, None.
        """
        return MKVUtils.get_program_path(MKVExtract.PROGRAM_NAME)


    @staticmethod
    def is_mkvextract_installed() -> bool:
        """
        Checks if the `mkvextract` program is installed and available in the system's PATH.

        Returns:
            True if `mkvextract` is installed, False otherwise.
        """
        return MKVExtract.get_program_path() is not None


    @staticmethod
    def verify_if_mkvextract_installed() -> None:
        """
        Verifies if the `mkvextract` program is installed. Raises an error if not found.

        Raises:
            Exception: If `mkvextract` is not found in the system's PATH.
        """
        if not MKVExtract.is_mkvextract_installed():
            raise Exception(
                f'{MKVExtract.PROGRAM_NAME} is isn\'t found. You need to correct your environnements variable or correctly install the program'
            )


    @staticmethod
    def get_mkv_font_files(mkv_file_path: Path, save_folder: Path) -> list[MKVFontFile]:
        """Extracts the fonts from an MKV file.

        Args:
            mkv_file_path (Path): The path to the MKV file.
            save_folder (Path): The folder where the font(s) will be saved.

        Returns:
            A list of extracted font file.
        """
        MKVExtract.verify_if_mkvextract_installed()
        MKVUtils.verify_if_file_mkv(mkv_file_path)

        cmd = [
            MKVExtract.get_program_path(),
            mkv_file_path,
            "attachments",
        ]

        mkv_font_files = []
        for attachment in MKVMerge.get_mkv_fonts_attachment(mkv_file_path):
            mkv_font_file = MKVFontFile(save_folder.joinpath(f"{attachment['id']}-{attachment['file_name']}"), attachment["id"], attachment["file_name"])
            cmd.append(f'{mkv_font_file.mkv_id}:{mkv_font_file.filename}')
            mkv_font_files.append(mkv_font_file)

        MKVUtils.run_command(MKVExtract.PROGRAM_NAME, cmd)
        return mkv_font_files


    @staticmethod
    def get_mkv_ass_files(mkv_file_path: Path, save_folder: Path) -> list[MKVASSFile]:
        """Extracts the .ass from an MKV file.

        Args:
            mkv_file_path (Path): The path to the MKV file.
            save_folder (Path): The folder where the ass file(s) will be saved.

        Returns:
            A list of extracted ass file.
        """
        MKVExtract.verify_if_mkvextract_installed()
        MKVUtils.verify_if_file_mkv(mkv_file_path)

        cmd = [
            MKVExtract.get_program_path(),
            mkv_file_path,
            "tracks",
        ]
        info = MKVMerge.get_mkv_info(mkv_file_path)
        mkv_ass_files = []

        for track in info["tracks"]:
            if track["properties"]["codec_id"] in MKVUtils.ASS_MIME_TYPE:
                mkv_ass_file = MKVASSFile(save_folder.joinpath(f"{track['id']}.ass"), track["id"], track["properties"].get("track_name", None))
                cmd.append(f'{mkv_ass_file.mkv_id}:{mkv_ass_file.filename}')
                mkv_ass_files.append(mkv_ass_file)


        MKVUtils.run_command(MKVExtract.PROGRAM_NAME, cmd)
        return mkv_ass_files
