import os
import pickle
from ._version import __version__
from .font import Font
from find_system_fonts_filename import get_system_fonts_filename
from pathlib import Path
from tempfile import gettempdir
from typing import List, Set, Iterable


class FontLoader:
    """
    system_fonts: Font installed on the system
    additional_fonts: Font added by the user
    generated_fonts: Contain all the generated font by Helpers.variable_font_to_collection.
    """

    system_fonts: Set[Font]
    additional_fonts: Set[Font]

    def __init__(
        self,
        additional_fonts_path: Iterable[Path] = [],
        use_system_font: bool = True,
        additional_fonts_path_recursive: Iterable[Path] = []
    ):

        if use_system_font:
            self.system_fonts = FontLoader.load_system_fonts()
        else:
            self.system_fonts = set()

        self.additional_fonts = FontLoader.load_additional_fonts(additional_fonts_path_recursive, scan_subdirs=True)
        self.additional_fonts.update(FontLoader.load_additional_fonts(additional_fonts_path, scan_subdirs=False))

    @property
    def fonts(self) -> Set[Font]:
        """
        Get all the fonts
        """
        return self.system_fonts.union(FontLoader.load_generated_fonts()).union(self.additional_fonts)

    def add_additional_font(self, font_path: Path):
        """
        Parameters:
            font_path (Path): Font path. The font can be a .ttf, .otf, .ttc or .otc
                If you need to use woff font, you will need to decompress them.
                See fontTools documentation to know how to do it: https://fonttools.readthedocs.io/en/latest/ttLib/woff2.html#fontTools.ttLib.woff2.decompress
        """
        self.additional_fonts.update(FontLoader.load_additional_fonts([font_path]))

    @staticmethod
    def add_generated_font(font: Font):
        """
        Parameters:
            font (Font): Generated font by Helpers.variable_font_to_collection
        """

        generated_fonts = FontLoader.load_generated_fonts()
        generated_fonts.add(font)
        FontLoader.save_generated_fonts(generated_fonts)

    @staticmethod
    def load_font_cache_file(cache_file: Path) -> Set[Font]:
        if not os.path.isfile(cache_file):
            raise FileNotFoundError(f'The file "{cache_file}" does not exist')

        with open(cache_file, "rb") as file:
            file_content = pickle.load(file)

        if isinstance(file_content, set):
            # previous version to 2.1.3 (included) was saving a set of fonts
            os.remove(cache_file)
            return set()
        elif isinstance(file_content, tuple) and len(file_content) == 2:
            font_collector_cache_version, cached_fonts = file_content

            if font_collector_cache_version != __version__:
                os.remove(cache_file)
                return set()

            return cached_fonts
        raise FileExistsError(f'The file "{cache_file}" contain invalid data')

    @staticmethod
    def save_font_cache_file(cache_file: Path, cache_fonts: Set[Font]) -> None:
        with open(cache_file, "wb") as file:
            pickle.dump((__version__, cache_fonts), file)

    @staticmethod
    def load_system_fonts() -> Set[Font]:
        system_fonts: Set[Font] = set()
        fonts_paths: Set[str] = get_system_fonts_filename()
        system_font_cache_file = FontLoader.get_system_font_cache_file_path()

        if os.path.isfile(system_font_cache_file):
            cached_fonts: Set[Font] = FontLoader.load_font_cache_file(system_font_cache_file)
            cached_paths = set(map(lambda font: font.filename, cached_fonts))

            # Remove font that aren't anymore installed
            removed = cached_paths.difference(fonts_paths)
            system_fonts = set(
                filter(lambda font: font.filename not in removed, cached_fonts)
            )

            # Add font that have been installed since last execution
            added = fonts_paths.difference(cached_paths)
            for font_path in added:
                system_fonts.update(Font.from_font_path(font_path))

            # If there is a change, update the cache file
            if len(added) > 0 or len(removed) > 0:
                FontLoader.save_font_cache_file(system_font_cache_file, system_fonts)

        else:
            # Since there is no cache file, load the font
            for font_path in fonts_paths:
                system_fonts.update(Font.from_font_path(font_path))

            # Save the font into the cache file
            FontLoader.save_font_cache_file(system_font_cache_file, system_fonts)

        return system_fonts

    @staticmethod
    def load_generated_fonts() -> Set[Font]:
        generated_fonts: Set[Font] = set()
        generated_font_cache_file = FontLoader.get_generated_font_cache_file_path()

        if os.path.isfile(generated_font_cache_file):
            cached_fonts: Set[Font] = FontLoader.load_font_cache_file(generated_font_cache_file)
            generated_fonts = set(filter(lambda font: os.path.isfile(font.filename), cached_fonts))

        return generated_fonts

    @staticmethod
    def load_additional_fonts(additional_fonts_path: Iterable[Path], scan_subdirs=False) -> Set[Font]:
        def is_file_font(file_name: Path):
            return file_name.suffix.lstrip(".").strip().lower() in ["ttf", "otf", "ttc", "otc"]

        additional_fonts: Set[Font] = set()

        for font_path in additional_fonts_path:
            if os.path.isfile(font_path):
                additional_fonts.update(Font.from_font_path(font_path))
            elif os.path.isdir(font_path):
                if scan_subdirs:
                    for root, dirs, files in os.walk(font_path):
                        for name in files:
                            file_path = os.path.join(root, name)
                            if is_file_font(Path(file_path)):
                                additional_fonts.update(Font.from_font_path(file_path))

                else:
                    for file in os.listdir(font_path):
                        file_path = os.path.join(font_path, file)
                        if is_file_font(Path(file_path)):
                            additional_fonts.update(Font.from_font_path(file_path))
            else:
                raise FileNotFoundError(f"The file {font_path} is not reachable")
        return additional_fonts

    @staticmethod
    def save_generated_fonts(generated_fonts: Set[Font]):
        generated_font_cache_file = FontLoader.get_generated_font_cache_file_path()
        FontLoader.save_font_cache_file(generated_font_cache_file, generated_fonts)

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
