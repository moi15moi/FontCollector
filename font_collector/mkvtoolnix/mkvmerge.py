from .utils import MKVUtils
import json
from pathlib import Path
from typing import Any

__all__ = ["MKVMerge"]


class MKVMerge:
    """
    This class is a collection of static methods that will help
    the user to interact with mkvmerge.
    """

    PROGRAM_NAME = "mkvmerge"
    PROGRAM_PATH = MKVUtils.get_program_path(PROGRAM_NAME)

    @staticmethod
    def is_mkvmerge_installed() -> bool:
        """
        Checks if the `mkvmerge` program is installed and available in the system's PATH.

        Returns:
            True if `mkvmerge` is installed, False otherwise.
        """
        return MKVMerge.PROGRAM_PATH is not None


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
    def get_version() -> tuple[int, int]:
        """Retrieves the version of `mkvmerge`.

        Equivalent to running: `mkvmerge --version`

        Returns:
            The major and minor version numbers of `mkvmerge`.
        """
        MKVMerge.verify_if_mkvmerge_installed()

        return MKVUtils.get_version(MKVMerge.PROGRAM_NAME, MKVMerge.PROGRAM_PATH) # type: ignore


    @staticmethod
    def get_mkv_info(mkv_file_path: Path) -> Any:
        """Retrieves information about an MKV file in JSON format.

        Equivalent to running: `mkvmerge FILE.mkv -J`

        Parameters:
            mkv_file_path (Path): The path to the MKV file.

        Returns:
            The information about the MKV file in JSON format.
        """
        MKVMerge.verify_if_mkvmerge_installed()
        MKVUtils.verify_if_file_mkv(mkv_file_path)

        cmd = [
            MKVMerge.PROGRAM_PATH,
            mkv_file_path,
            "-J",
        ]

        mkvmerge_output = MKVUtils.run_command(MKVMerge.PROGRAM_NAME, cmd)
        mkvmerge_output_dict = json.loads(mkvmerge_output.stdout)

        return mkvmerge_output_dict
