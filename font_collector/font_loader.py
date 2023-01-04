import os
import pickle
from .font import Font
from matplotlib import font_manager
from pathlib import Path
from tempfile import gettempdir
from typing import List, Set


class FontLoader:
    system_fonts: Set[Font]
    additional_fonts: Set[Font]

    def __init__(
        self, additional_fonts_path: List[Path] = [], use_system_font: bool = True
    ):

        if use_system_font:
            self.system_fonts = FontLoader.load_system_fonts()
        else:
            self.system_fonts = set()

        self.additional_fonts = FontLoader.load_additional_fonts(additional_fonts_path)

    @property
    def fonts(self) -> Set[Font]:
        """
        Get all the fonts
        """
        return self.system_fonts.union(FontLoader.load_generated_fonts()).union(
            self.additional_fonts
        )

    def add_additional_font(self, font_path: Path):
        self.additional_fonts.update(FontLoader.load_additional_fonts([font_path]))

    def add_generated_font(self, font: Font):
        generated_fonts = FontLoader.load_generated_fonts()
        generated_fonts.add(font)
        FontLoader.save_generated_fonts(generated_fonts)

    @staticmethod
    def load_system_fonts() -> Set[Font]:
        system_fonts: Set[Font] = set()
        fonts_paths: Set[str] = set(font_manager.findSystemFonts())
        system_font_cache_file = FontLoader.get_system_font_cache_file_path()

        if os.path.exists(system_font_cache_file):

            with open(system_font_cache_file, "rb") as file:
                cached_fonts: Set[Font] = pickle.load(file)

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
                with open(system_font_cache_file, "wb") as file:
                    pickle.dump(system_fonts, file)

        else:
            # Since there is no cache file, load the font
            for font_path in fonts_paths:
                system_fonts.update(Font.from_font_path(font_path))

            # Save the font into the cache file
            with open(system_font_cache_file, "wb") as file:
                pickle.dump(system_fonts, file)

        return system_fonts

    @staticmethod
    def load_generated_fonts() -> Set[Font]:
        generated_fonts: Set[Font] = set()
        generated_font_cache_file = FontLoader.get_generated_font_cache_file_path()

        if os.path.exists(generated_font_cache_file):
            with open(generated_font_cache_file, "rb") as file:
                cached_fonts: Set[Font] = pickle.load(file)

            generated_fonts = set(
                filter(lambda font: os.path.exists(font.filename), cached_fonts)
            )

        return generated_fonts

    @staticmethod
    def load_additional_fonts(additional_fonts_path: List[Path]) -> Set[Font]:
        additional_fonts: Set[Font] = set()

        for font_path in additional_fonts_path:
            if os.path.isfile(font_path):
                additional_fonts.update(Font.from_font_path(font_path))
            elif os.path.isdir(font_path):
                additional_fonts.update(
                    [
                        Font.from_font_path(path)
                        for path in font_manager.findSystemFonts(
                            fontpaths=str(font_path)
                        )
                    ]
                )
            else:
                raise FileNotFoundError(f"The file {font_path} is not reachable")
        return additional_fonts

    @staticmethod
    def save_generated_fonts(generated_fonts: Set[Font]):
        generated_font_cache_file = FontLoader.get_generated_font_cache_file_path()
        with open(generated_font_cache_file, "wb") as file:
            pickle.dump(generated_fonts, file)

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
