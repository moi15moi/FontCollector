import logging
import os
from .parse_font import ParseFont
from fontTools.ttLib.ttFont import TTFont
from fontTools.ttLib.ttCollection import TTCollection
from typing import List, Sequence, Set

_logger = logging.getLogger(__name__)


class Font:
    filename: str
    font_index: int
    __family_names: Set[str]
    weight: int
    italic: bool
    __exact_names: Set[
        str
    ]  # if the font is a TrueType, it will be the "full_name". if the font is a OpenType, it will be the "postscript name"
    is_var: bool

    def __init__(
        self,
        filename: str,
        font_index: int,
        family_names: Set[str],
        weight: int,
        italic: bool,
        exact_names: Set[str],
        is_var: bool,
    ):
        self.filename = filename
        self.font_index = font_index
        self.family_names = family_names
        self.weight = weight
        self.italic = italic
        self.exact_names = exact_names
        self.is_var = is_var

    @classmethod
    def from_font_path(cls, font_path: str) -> List["Font"]:
        """
        Parameters:
            font_path (str): Font path. The font can be a .ttf, .otf or .ttc
        Returns:
            An Font object that represent the file at the font_path
        """
        ttFonts: List[TTFont] = []
        fonts: List[Font] = []

        with open(font_path, "rb") as font_file:
            if ParseFont.is_file_truetype_collection(font_file):
                ttFonts.extend(TTCollection(font_path).fonts)
            elif ParseFont.is_file_truetype(font_file) or ParseFont.is_file_opentype(
                font_file
            ):
                ttFonts.append(TTFont(font_path))
            else:
                raise FileExistsError(
                    f'The file "{font_path}" is not a valid font file'
                )

        try:

            # Read font attributes
            for font_index, ttFont in enumerate(ttFonts):

                families = set()
                exact_names = set()

                # If is Variable Font, else "normal" font
                if is_var := ("fvar" in ttFont and "STAT" in ttFont):

                    for instance in ttFont["fvar"].instances:
                        axis_value_tables = ParseFont.get_axis_value_from_coordinates(
                            ttFont, instance.coordinates
                        )
                        (
                            family_name,
                            full_font_name,
                        ) = ParseFont.get_var_font_family_fullname(
                            ttFont, axis_value_tables
                        )

                        families.add(family_name)
                        families.add(full_font_name)

                else:
                    # From https://github.com/fonttools/fonttools/discussions/2619
                    is_truetype = "glyf" in ttFont

                    families, fullnames = ParseFont.get_font_family_fullname_property(
                        ttFont["name"].names
                    )

                    # This is something like: https://github.com/libass/libass/blob/a2b39cde4ecb74d5e6fccab4a5f7d8ad52b2b1a4/libass/ass_fontselect.c#L303-L311
                    if len(families) == 0:
                        familyName = ParseFont.get_name_by_id(1, ttFont["name"].names)

                        if familyName:
                            families.add(familyName)
                        else:
                            # Skip the font since it is invalid
                            _logger.info(
                                f'Warning: The index {font_index} of the font "{font_path}" does not contain an valid family name. The font index will be ignored.'
                            )
                            continue

                    if is_truetype:
                        exact_names = fullnames
                    else:
                        # If not TrueType, it is OpenType

                        postscript_name = ParseFont.get_font_postscript_property(
                            font_path, font_index
                        )
                        if postscript_name is not None:
                            exact_names.add(postscript_name)

                is_italic, weight = ParseFont.get_font_italic_bold_property(
                    ttFont, font_path, font_index
                )
                fonts.append(
                    Font(
                        font_path,
                        font_index,
                        families,
                        weight,
                        is_italic,
                        exact_names,
                        is_var,
                    )
                )
        except Exception:
            _logger.error(f'An unknown error occurred while reading the font "{font_path}"{os.linesep}Please open an issue on github, share the font and the following error message:')
            raise
        return fonts

    @property
    def family_names(self):
        return self.__family_names

    @family_names.setter
    def family_names(self, family_names: List[str]):
        self.__family_names = set([family_name.lower() for family_name in family_names])

    @property
    def exact_names(self):
        return self.__exact_names

    @exact_names.setter
    def exact_names(self, exact_names: List[str]):
        self.__exact_names = set([exact_name.lower() for exact_name in exact_names])

    def __eq__(self, other: "Font"):
        return (self.family_names, self.weight, self.italic, self.exact_names) == (
            other.family_names,
            other.weight,
            other.italic,
            other.exact_names,
        )

    def __hash__(self):
        return hash(
            (
                tuple(self.family_names),
                self.italic,
                self.weight,
                tuple(self.exact_names),
            )
        )

    def __repr__(self):
        return f'Filename: "{self.filename}" Family_names: "{self.family_names}", Weight: "{self.weight}", Italic: "{self.italic}, Exact_names: "{self.exact_names}"'

    def get_missing_glyphs(self, text: Sequence[str]):

        ttFont = TTFont(self.filename, fontNumber=self.font_index)

        char_not_found: Set[str] = set()

        for char in text:
            char_found = False
            for table in ttFont["cmap"].tables:
                if ord(char) in table.cmap:
                    char_found = True
                    break
            if not char_found:
                char_not_found.add(char)

        return char_not_found
