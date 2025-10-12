import json
from pathlib import Path
from typing import Any, Optional

from .mkv_utils import MKVUtils

__all__ = ["MKVMerge"]


class MKVMerge:
    """
    This class is a collection of static methods that will help
    the user to interact with mkvmerge.
    """

    PROGRAM_NAME = "mkvmerge"

    @staticmethod
    def get_program_path() -> Optional[Path]:
        """
        Retrieves the full path to the `mkvmerge` executable.

        Returns:
            If found, the path to `mkvmerge`. Otherwise, None.
        """
        return MKVUtils.get_program_path(MKVMerge.PROGRAM_NAME)


    @staticmethod
    def is_mkvmerge_installed() -> bool:
        """
        Checks if the `mkvmerge` program is installed and available in the system's PATH.

        Returns:
            True if `mkvmerge` is installed, False otherwise.
        """
        return MKVMerge.get_program_path() is not None


    @staticmethod
    def verify_if_mkvmerge_installed() -> None:
        """
        Verifies if the `mkvmerge` program is installed. Raises an error if not found.

        Raises:
            Exception: If `mkvmerge` is not found in the system's PATH.
        """
        if not MKVMerge.is_mkvmerge_installed():
            raise Exception(f'{MKVMerge.PROGRAM_NAME} is isn\'t found. You need to correct your environnements variable or correctly install the program')


    @staticmethod
    def get_mkv_info(mkv_file_path: Path) -> Any:
        """Retrieves information about an MKV file in JSON format.

        Equivalent to running: `mkvmerge FILE.mkv -J`

        Args:
            mkv_file_path (Path): The path to the MKV file.

        Returns:
            The information about the MKV file in JSON format.
        """
        MKVMerge.verify_if_mkvmerge_installed()
        MKVUtils.verify_if_file_mkv(mkv_file_path)

        cmd = [
            MKVMerge.get_program_path(),
            mkv_file_path,
            "-J",
        ]
        mkvmerge_output = MKVUtils.run_command(MKVMerge.PROGRAM_NAME, cmd)
        mkvmerge_output_dict = json.loads(mkvmerge_output.stdout)

        return mkvmerge_output_dict


    @staticmethod
    def get_mkv_fonts_attachment(mkv_file_path: Path) -> list[Any]:
        """Retrieves information about the font attached to a mkv

        Equivalent to running: `mkvmerge FILE.mkv -J` and
        using a filter on the "attachments" section to retrieve only the fonts.

        Args:
            mkv_file_path (Path): The path to the MKV file.

        Returns:
            The information about the attached font(s) to the mkv in JSON format.
        """
        info = MKVMerge.get_mkv_info(mkv_file_path)

        # Extract the font like the spec says: https://github.com/ietf-wg-cellar/matroska-specification/blob/20d36395f94d85485e39988d602652781740420a/cellar-matroska/attachments.md?plain=1#L87-L111
        attachments = []
        for attachment in info["attachments"]:
            if (
                attachment["content_type"] in MKVUtils.FONT_MIME_TYPE or
                (
                    attachment["content_type"] == "application/octet-stream" and
                    attachment["file_name"].lower().endswith((".ttf", ".otf", ".ttc", ".otc"))
                )
            ):
                attachments.append(attachment)

        return attachments
