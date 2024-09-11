from typing import List

from .mkv_ass_file import MKVASSFile

from .auto_delete_path import AutoDeletePath
from .mkv_font_file import MKVFontFile
from .mkvmerge import MKVMerge
from .utils import MKVUtils
from tempfile import NamedTemporaryFile, TemporaryDirectory, gettempdir
from pathlib import Path

__all__ = ["MKVExtract"]


class MKVExtract:
    """
    This class is a collection of static methods that will help
    the user to interact with mkvextract.
    """

    PROGRAM_NAME = "mkvextract"
    PROGRAM_PATH = MKVUtils.get_program_path(PROGRAM_NAME)

    @staticmethod
    def is_mkvextract_installed() -> bool:
        """
        Checks if the `mkvextract` program is installed and available in the system's PATH.

        Returns:
            True if `mkvextract` is installed, False otherwise.
        """
        return MKVExtract.PROGRAM_PATH is not None


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
    def get_mkv_font_files(mkv_file_path: Path) -> List[MKVFontFile]:
        """Extracts the timestamps from an MKV file for a specific track index.

        Parameters:
            mkv_file_path (Path): The path to the MKV file.
            index (int): Index of the video stream.

        Returns:
            The content of the timestamps file.
        """

        MKVExtract.verify_if_mkvextract_installed()
        MKVUtils.verify_if_file_mkv(mkv_file_path)


        cmd = [
            MKVExtract.PROGRAM_PATH,
            mkv_file_path,
            "attachments",
        ]

        info = MKVMerge.get_mkv_info(mkv_file_path)

        mkv_font_files = []

        for attachment in info["attachments"]:
            if attachment["content_type"] in MKVUtils.FONT_MIME_TYPE:
                mkv_font_file = MKVFontFile(AutoDeletePath(NamedTemporaryFile().name), attachment["id"], attachment["file_name"])
                cmd.append(f'{mkv_font_file.mkv_id}:{mkv_font_file.filename.path}')
                mkv_font_files.append(mkv_font_file)


        MKVUtils.run_command(MKVExtract.PROGRAM_NAME, cmd)
        return mkv_font_files

    @staticmethod
    def get_mkv_ass_files(mkv_file_path: Path) -> List[MKVASSFile]:
        """Extracts the timestamps from an MKV file for a specific track index.

        Parameters:
            mkv_file_path (Path): The path to the MKV file.
            index (int): Index of the video stream.

        Returns:
            The content of the timestamps file.
        """

        MKVExtract.verify_if_mkvextract_installed()
        MKVUtils.verify_if_file_mkv(mkv_file_path)


        cmd = [
            MKVExtract.PROGRAM_PATH,
            mkv_file_path,
            "tracks",
        ]

        info = MKVMerge.get_mkv_info(mkv_file_path)

        mkv_ass_files = []

        for attachment in info["tracks"]:
            if attachment["properties"]["codec_id"] in MKVUtils.ASS_MIME_TYPE:
                mkv_ass_file = MKVASSFile(AutoDeletePath(NamedTemporaryFile().name), attachment["id"])
                cmd.append(f'{mkv_ass_file.mkv_id}:{mkv_ass_file.filename.path}')
                mkv_ass_files.append(mkv_ass_file)


        MKVUtils.run_command(MKVExtract.PROGRAM_NAME, cmd)
        return mkv_ass_files
