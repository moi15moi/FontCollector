from __future__ import annotations
import logging
import os
import pickle
from ..exceptions import InvalidFontException
from .._version import __version__
from .font_file import FontFile
from find_system_fonts_filename import get_system_fonts_filename
from pathlib import Path
from tempfile import gettempdir

from collections.abc import Iterable

__all__ = ["FontLoader"]
_logger = logging.getLogger(__name__)


class CacheFileContent:
    """Represents the content structure of a font cache file.

    Attributes:
        font_collector_version: The version of the font collector that created the cache.
        cached_fonts: A list of FontFile objects representing the cached fonts.
    """
    def __init__(self, font_collector_version: str, cached_fonts: list[FontFile]):
        self.font_collector_version = font_collector_version
        self.cached_fonts = cached_fonts


class FontLoader:
    """
    This class is a collection of static methods that will help
    the user to load the font file from a various source.
    """

    @staticmethod
    def load_font_cache_file(cache_file: Path) -> list[FontFile]:
        """Load the cache file and retrieve the list of cached fonts from it.
        Note: If the cache file is invalid, the file will be deleted

        Args:
            cache_file: The path to the font cache file.
        Returns:
            A list of FontFile objects representing the cached fonts.
        """

        cached_fonts: list[FontFile] = []
        if not cache_file.is_file():
            raise FileNotFoundError(f'The file "{cache_file}" does not exist')

        has_failed_to_read_cache = False
        with open(cache_file, "rb") as file:
            try:
                file_content = pickle.load(file)
            except Exception:
                has_failed_to_read_cache = True

        if has_failed_to_read_cache:
            cache_file.unlink()
            return cached_fonts

        if isinstance(file_content, CacheFileContent):
            cache_file_content = file_content

            if cache_file_content.font_collector_version == __version__:
                cached_fonts = cache_file_content.cached_fonts
            else:
                cache_file.unlink()
        else:
            cache_file.unlink()

        return cached_fonts


    @staticmethod
    def save_font_cache_file(cache_file: Path, cache_fonts: list[FontFile]) -> None:
        """Serialize and save the font cache data to a specified file.

        This method creates a cache file with the provided path and stores the font cache data.
        If the cache file already exists, it will be overwritten.

        Args:
            cache_file: The path to the font cache file.
            cache_fonts: A list of FontFile objects representing the font cache.
        """
        with open(cache_file, "wb") as file:
            pickle.dump(CacheFileContent(__version__, cache_fonts), file)


    @staticmethod
    def load_additional_fonts(additional_fonts_path: Iterable[Path], scan_subdirs: bool = False) -> list[FontFile]:
        """Load additional fonts from the specified paths, including subdirectories if specified.

        Args:
            additional_fonts_path: Iterable of font file path or directory paths.
                If you have specified a directory, it will only try to load files with the following extensions: ttf, otf, ttc, and otc.
            scan_subdirs: If True, it will scan subdirectories for the directory specified in additional_fonts_path.
                If False, it will only scan the directory specified in additional_fonts_path.
        Returns:
            A list of FontFile objects representing the loaded fonts.
        """
        def is_file_font(file_name: Path) -> bool:
            return file_name.suffix.lstrip(".").strip().casefold() in ["ttf", "otf", "ttc", "otc"]

        additional_fonts: list[FontFile] = []

        for font_path in additional_fonts_path:
            if font_path.is_file():
                try:
                    additional_fonts.append(FontFile.from_font_path(font_path))
                except InvalidFontException as e:
                    _logger.info(f"{e}. The font {font_path} will be ignored.")
            elif font_path.is_dir():
                if scan_subdirs:
                    for root, dirs, files in os.walk(font_path):
                        for name in files:
                            file_path = Path(os.path.join(root, name))
                            if is_file_font(file_path):
                                try:
                                    additional_fonts.append(FontFile.from_font_path(file_path))
                                except InvalidFontException as e:
                                    _logger.info(f"{e}. The font {file_path} will be ignored.")
                else:
                    for path in font_path.iterdir():
                        if path.is_file() and is_file_font(path):
                            try:
                                additional_fonts.append(FontFile.from_font_path(path))
                            except InvalidFontException as e:
                                _logger.info(f"{e}. The font {path} will be ignored.")
            else:
                raise FileNotFoundError(f"The file or directory {font_path} is not reachable")
        return additional_fonts


    @staticmethod
    def load_system_fonts() -> list[FontFile]:
        """
        Returns:
            A list of FontFile objects representing the system fonts.
        """
        system_fonts: list[FontFile] = []
        fonts_paths: set[Path] = {Path(font_path) for font_path in get_system_fonts_filename()}
        system_font_cache_file = FontLoader.get_system_font_cache_file_path()

        if system_font_cache_file.is_file():
            cached_fonts = FontLoader.load_font_cache_file(system_font_cache_file)
            cached_paths = set(map(lambda item: item.filename, cached_fonts))

            # Remove font that aren't anymore installed
            removed_path = cached_paths.difference(fonts_paths)
            system_fonts = list(filter(lambda item: item.filename not in removed_path, cached_fonts))

            # Update font that have been updated since last execution
            has_updated_font = False
            for cached_font in system_fonts:
                if cached_font.filename.stat().st_ctime > cached_font.last_loaded_time:
                    cached_font.reload_font_file()
                    has_updated_font = True

            # Add font that have been installed since last execution
            added_path = fonts_paths.difference(cached_paths)
            for font_path in added_path:
                try:
                    system_fonts.append(FontFile.from_font_path(font_path))
                except InvalidFontException as e:
                    _logger.info(f"{e}. The font {font_path} will be ignored.")

            # If there is a change, update the cache file
            if len(added_path) > 0 or len(removed_path) > 0 or has_updated_font:
                FontLoader.save_font_cache_file(system_font_cache_file, system_fonts)

        else:
            # Since there is no cache file, load the font
            for font_path in fonts_paths:
                try:
                    system_fonts.append(FontFile.from_font_path(font_path))
                except InvalidFontException as e:
                    _logger.info(f"{e}. The font {font_path} will be ignored.")

            # Save the font into the cache file
            FontLoader.save_font_cache_file(system_font_cache_file, system_fonts)

        return system_fonts


    @staticmethod
    def load_generated_fonts() -> list[FontFile]:
        """
        Returns:
            A list of FontFile objects representing the generated fonts.
            These fonts are created when the user converts a variable font to a normal font
                via the VariableFontFace.variable_font_to_collection() method.
        """
        generated_fonts: list[FontFile] = []
        generated_font_cache_file = FontLoader.get_generated_font_cache_file_path()

        if generated_font_cache_file.is_file():
            cached_fonts = FontLoader.load_font_cache_file(generated_font_cache_file)
            generated_fonts = list(filter(lambda cached_font: cached_font.filename.is_file(), cached_fonts))
            has_deleted_font = len(cached_fonts) != len(generated_fonts)

            has_updated_font = False
            # Update font that have been updated since last execution
            for cached_font in generated_fonts:
                if cached_font.filename.stat().st_ctime > cached_font.last_loaded_time:
                    cached_font.reload_font_file()
                    has_updated_font = True

            if has_deleted_font > 0 or has_updated_font:
                FontLoader.save_font_cache_file(generated_font_cache_file, generated_fonts)

        return generated_fonts


    @staticmethod
    def add_generated_font(font: FontFile) -> None:
        """
        Args:
            font: The generated font obtained from VariableFontFace.variable_font_to_collection().
                This font will be cached and subsequently loaded when FontLoader.load_generated_fonts() is called.
        """
        generated_fonts = FontLoader.load_generated_fonts()
        generated_fonts.append(font)
        FontLoader.save_font_cache_file(FontLoader.get_generated_font_cache_file_path(), generated_fonts)


    @staticmethod
    def discard_system_font_cache() -> None:
        """
        Discards the system font cache if it exists.
        """
        system_font_cache = FontLoader.get_system_font_cache_file_path()
        if system_font_cache.is_file():
            system_font_cache.unlink()


    @staticmethod
    def discard_generated_font_cache() -> None:
        """
        Discards the generated font cache if it exists.
        """
        generated_font_cache = FontLoader.get_generated_font_cache_file_path()
        if generated_font_cache.is_file():
            generated_font_cache.unlink()


    @staticmethod
    def get_system_font_cache_file_path() -> Path:
        """
        Returns:
            The path to the system font cache file.
            Warning, the file may not exist.
        """
        tempDir = gettempdir()
        return Path(os.path.join(tempDir, "FontCollector_SystemFont.bin"))


    @staticmethod
    def get_generated_font_cache_file_path() -> Path:
        """
        Returns:
            The path to the generated font cache file.
            Warning, the file may not exist.
        """
        tempDir = gettempdir()
        return Path(os.path.join(tempDir, "FontCollector_GeneratedFont.bin"))
