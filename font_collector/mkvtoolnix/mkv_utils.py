import os
import subprocess
from pathlib import Path
from platform import system
from shutil import which
from subprocess import CompletedProcess
from typing import Any, Optional
from warnings import warn

from .exit_code import ExitCode

__all__ = ["MKVUtils"]


class MKVUtils():
    """
    A utility class for interacting with MKV files and MKVToolNix command-line tools.

    Provides methods to verify MKV files, locate MKVToolNix programs, run commands, and extract version information.
    """

    # This is from mpv: https://github.com/mpv-player/mpv/blob/c438732b239bf4e7f3d574f8fcc141f92366018a/sub/sd_ass.c#L133-L145
    FONT_MIME_TYPE = [
        "application/x-truetype-font",
        "application/vnd.ms-opentype",
        "application/x-font-otf",
        "application/x-font-ttf",
        "application/x-font",
        "application/font-sfnt",
        "font/collection",
        "font/otf",
        "font/sfnt",
        "font/ttf"
    ]

    # This is from mpv: https://github.com/mpv-player/mpv/blob/c438732b239bf4e7f3d574f8fcc141f92366018a/demux/demux_mkv.c#L1821-L1824
    ASS_MIME_TYPE = [
        "S_TEXT/SSA",
        "S_TEXT/ASS",
        "S_SSA",
        "S_ASS"
    ]

    MKVTOOLNIX_FOLDER: Path | None = None


    @staticmethod
    def is_mkv(file: Path) -> bool:
        """
        Args:
            file (Path): The path to the file.
        Returns:
            True if the file is an MKV file, False otherwise.
        """

        if not file.is_file():
            raise FileNotFoundError(f'"{file}" isn\'t a file or does not exist.')

        with open(file, "rb") as f:
            # From https://en.wikipedia.org/wiki/List_of_file_signatures
            return f.read(4) == b"\x1a\x45\xdf\xa3"


    @staticmethod
    def verify_if_file_mkv(file: Path) -> None:
        """
        Args:
            file (Path): The path to the file.

        Raises:
            FileExistsError: If the file is not an MKV file.
        """

        if not MKVUtils.is_mkv(file):
            raise FileExistsError(f'The file "{file}" is not an mkv file.')


    @staticmethod
    def get_program_path(program_name: str) -> Path | None:
        """Retrieves the full path of the specified program.

        Args:
            program_name (str): The name of the program (ex: "mkvextract").

        Returns:
            The full path of the program if found, None otherwise.
        """
        if MKVUtils.MKVTOOLNIX_FOLDER:
            if not MKVUtils.MKVTOOLNIX_FOLDER.is_dir():
                raise FileNotFoundError(f"The mkvtoolnix folder \"{MKVUtils.MKVTOOLNIX_FOLDER}\" doesn't exist.")

            if system() == "Windows":
                path = MKVUtils.MKVTOOLNIX_FOLDER.joinpath(f"{program_name}.exe")
            else:
                path = MKVUtils.MKVTOOLNIX_FOLDER.joinpath(program_name)

            if not path.is_file():
                raise FileNotFoundError(f"The program {program_name} should be located at \"{path}\" but it isn't.")

            return path

        program_path = which(program_name)
        if program_path:
            return Path(program_path)

        if system() == "Windows":
            possible_dirs = [
                os.environ.get("ProgramFiles"),
                os.environ.get("ProgramFiles(x86)")
            ]

            for base_dir in possible_dirs:
                if base_dir: # only if environment variable is set
                    path = Path(base_dir).joinpath("MKVToolNix", f"{program_name}.exe")
                    if path.is_file():
                        return path

        return None


    @staticmethod
    def verify_if_command_fails(program_name: str, output: CompletedProcess[str]) -> None:
        """Checks the result of a command execution and raises an error or warning based on the exit code.

        Args:
            program_name (str): The name of the program that was run (ex: "mkvextract").
            output (CompletedProcess): The result of the command execution.

        Raises:
            OSError: If the command reported an error.
            Warning: If the command reported a warning.
        """
        if output.returncode == ExitCode.ERROR:
            raise OSError(f"{program_name} reported an error: '{output.stdout}'.")
        elif output.returncode == ExitCode.WARNING:
            warn(f"{program_name} reported an warning '{output.stdout}'.")


    @staticmethod
    def run_command(program_name: str, cmd: list[Any]) -> CompletedProcess[str]:
        """Runs a command and verifies if it fails.

        Args:
            program_name (str): The name of the program to be executed (e.g., "mkvextract").
            cmd (List[Any]): The command to be run, including its arguments.

        Returns:
            CompletedProcess: The result of the command execution.
        """
        cmd.extend([
            "--output-charset", "UTF-8",
        ])

        output = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        MKVUtils.verify_if_command_fails(program_name, output)
        return output
