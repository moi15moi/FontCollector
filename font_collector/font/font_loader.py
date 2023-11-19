import logging
import os
import pickle
import time
from ..exceptions import InvalidFontException
from .._version import __version__
from .abc_font import ABCFont
from .factory_abc_font import FactoryABCFont
from find_system_fonts_filename import get_system_fonts_filename
from pathlib import Path
from tempfile import gettempdir
from typing import Iterable, List, Set

_logger = logging.getLogger(__name__)


class CacheFont:
    font: ABCFont
    last_loaded_time: float

    def __init__(self, font: ABCFont, last_loaded_time: float):
        self.font = font
        self.last_loaded_time = last_loaded_time


class CacheFileContent:
    font_collector_version: str
    cached_fonts: List[CacheFont]

    def __init__(self, font_collector_version: str, cached_fonts: List[CacheFont]):
        self.font_collector_version = font_collector_version
        self.cached_fonts = cached_fonts


class FontLoader:

    @staticmethod
    def load_font_cache_file(cache_file: Path) -> List[CacheFont]:
        if not os.path.isfile(cache_file):
            raise FileNotFoundError(f'The file "{cache_file}" does not exist')

        with open(cache_file, "rb") as file:
            # TODO add try except. If fail, os.remove(cache_file)
            file_content = pickle.load(file)

        if isinstance(file_content, CacheFileContent):
            cache_file_content = file_content

            if cache_file_content.font_collector_version != __version__:
                os.remove(cache_file)
                return set()

            return cache_file_content.cached_fonts

        # Remove file since it contain invalid data
        os.remove(cache_file)
        return set()


    @staticmethod
    def save_font_cache_file(cache_file: Path, cache_fonts: List[CacheFont]) -> None:
        with open(cache_file, "wb") as file:
            pickle.dump(CacheFileContent(__version__, cache_fonts), file)


    @staticmethod
    def load_additional_fonts(additional_fonts_path: Iterable[Path], scan_subdirs=False) -> Set[ABCFont]:
        def is_file_font(file_name: Path):
            return file_name.suffix.lstrip(".").strip().lower() in ["ttf", "otf", "ttc", "otc"]

        additional_fonts: Set[ABCFont] = set()

        for font_path in additional_fonts_path:
            if os.path.isfile(font_path):
                try:
                    additional_fonts.update(FactoryABCFont.from_font_path(font_path))
                except InvalidFontException as e:
                    _logger.info(f"{e}. The font {font_path} will be ignored.")
            elif os.path.isdir(font_path):
                if scan_subdirs:
                    for root, dirs, files in os.walk(font_path):
                        for name in files:
                            file_path = os.path.join(root, name)
                            if is_file_font(Path(file_path)):
                                try:
                                    additional_fonts.update(FactoryABCFont.from_font_path(file_path))
                                except InvalidFontException as e:
                                    _logger.info(f"{e}. The font {font_path} will be ignored.")
                else:
                    for file in os.listdir(font_path):
                        file_path = os.path.join(font_path, file)
                        if is_file_font(Path(file_path)):
                            try:
                                additional_fonts.update(FactoryABCFont.from_font_path(file_path))
                            except InvalidFontException as e:
                                _logger.info(f"{e}. The font {font_path} will be ignored.")
            else:
                raise FileNotFoundError(f"The file or directory {font_path} is not reachable")
        return additional_fonts


    @staticmethod
    def load_system_fonts() -> Set[ABCFont]:
        system_fonts: List[CacheFont] = []
        fonts_paths = get_system_fonts_filename()
        system_font_cache_file = FontLoader.get_system_font_cache_file_path()

        if os.path.isfile(system_font_cache_file):
            cached_fonts = FontLoader.load_font_cache_file(system_font_cache_file)
            cached_paths = set(map(lambda item: item.font.filename, cached_fonts))

            # Remove font that aren't anymore installed
            removed_path = cached_paths.difference(fonts_paths)
            system_fonts = list(filter(lambda item: item.font.filename not in removed_path, cached_fonts))
  
            # Update font that have been updated since last execution
            updated_path: List[os.PathLike[str]] = []
            updated_fonts: List[CacheFont] = []
            for cached_font in system_fonts:
                if os.path.getctime(cached_font.font.filename) > cached_font.last_loaded_time and cached_font.font.filename not in updated_path:
                    updated_path.append(cached_font.font.filename)
                    updated_fonts.extend([CacheFont(font, time.time()) for font in FactoryABCFont.from_font_path(cached_font.font.filename)])
            system_fonts = list(filter(lambda cached_font: cached_font.font.filename not in updated_path, system_fonts))
            system_fonts.extend(updated_fonts)

            # Add font that have been installed since last execution
            added_path = fonts_paths.difference(cached_paths)
            for font_path in added_path:
                try:
                    system_fonts.extend([CacheFont(font, time.time()) for font in FactoryABCFont.from_font_path(font_path)])
                except InvalidFontException as e:
                    _logger.info(f"{e}. The font {font_path} will be ignored.")

            # If there is a change, update the cache file
            if len(added_path) > 0 or len(removed_path) > 0 or len(updated_path) > 0:
                FontLoader.save_font_cache_file(system_font_cache_file, system_fonts)

        else:
            # Since there is no cache file, load the font
            for font_path in fonts_paths:
                try:
                    system_fonts.extend([CacheFont(font, time.time()) for font in FactoryABCFont.from_font_path(font_path)])
                except InvalidFontException as e:
                    _logger.info(f"{e}. The font {font_path} will be ignored.")

            # Save the font into the cache file
            FontLoader.save_font_cache_file(system_font_cache_file, system_fonts)

        return set([cached_font.font for cached_font in system_fonts])


    @staticmethod
    def _load_generated_fonts() -> List[CacheFont]:
        generated_fonts: List[CacheFont] = []
        generated_font_cache_file = FontLoader.get_generated_font_cache_file_path()

        if os.path.isfile(generated_font_cache_file):
            cached_fonts = FontLoader.load_font_cache_file(generated_font_cache_file)
            generated_fonts = list(filter(lambda cached_font: os.path.isfile(cached_font.font.filename), cached_fonts))

            # Update font that have been updated since last execution
            updated_path: List[os.PathLike[str]] = []
            updated_fonts: List[CacheFont] = []
            for cached_font in generated_fonts:
                if os.path.getctime(cached_font.font.filename) > cached_font.last_loaded_time and cached_font.font.filename not in updated_path:
                    updated_path.append(cached_font.font.filename)
                    updated_fonts.extend([CacheFont(font, time.time()) for font in FactoryABCFont.from_font_path(cached_font.font.filename)])
            generated_fonts = list(filter(lambda cached_font: cached_font.font.filename not in updated_path, generated_fonts))
            generated_fonts.extend(updated_fonts)

        return generated_fonts


    @staticmethod
    def load_generated_fonts() -> Set[ABCFont]:
        return set([cached_font.font for cached_font in FontLoader._load_generated_fonts()])


    @staticmethod
    def add_generated_font(font: ABCFont) -> None:
        """
        Parameters:
            font (Font): Generated font by Helpers.variable_font_to_collection
            It will be cached. 
        """
        generated_fonts = FontLoader._load_generated_fonts()
        generated_fonts.append(CacheFont(font, time.time()))
        FontLoader.save_font_cache_file(FontLoader.get_generated_font_cache_file_path(), generated_fonts)


    @staticmethod
    def discard_system_font_cache():
        system_font_cache = FontLoader.get_system_font_cache_file_path()
        if os.path.isfile(system_font_cache):
            os.remove(system_font_cache)


    @staticmethod
    def discard_generated_font_cache():
        generated_font_cache = FontLoader.get_generated_font_cache_file_path()
        if os.path.isfile(generated_font_cache):
            os.remove(generated_font_cache)


    @staticmethod
    def get_system_font_cache_file_path() -> Path:
        tempDir = gettempdir()
        return Path(os.path.join(tempDir, "FontCollector_SystemFont.bin"))


    @staticmethod
    def get_generated_font_cache_file_path() -> Path:
        tempDir = gettempdir()
        return Path(os.path.join(tempDir, "FontCollector_GeneratedFont.bin"))