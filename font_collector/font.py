import logging
import os
from .exceptions import InvalidFontException
from .font_parser import FontParser, NameID
from ctypes import byref
from fontTools.ttLib.ttFont import TTFont
from fontTools.ttLib.ttCollection import TTCollection
from freetype import (
    FT_Done_Face,
    FT_Done_FreeType,
    FT_Exception,
    FT_Face,
    FT_Get_Char_Index,
    FT_Get_CMap_Format,
    FT_Init_FreeType,
    FT_Library,
    FT_New_Memory_Face,
    FT_Set_Charmap,
)
from typing import Any, Dict, List, Sequence, Set, Tuple

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
    named_instance_coordinates: Dict[str, float] = {}

    def __init__(
        self,
        filename: str,
        font_index: int,
        family_names: Sequence[str],
        weight: int,
        italic: bool,
        exact_names: Sequence[str],
        named_instance_coordinates: Dict[str, float] = {},
    ):
        self.filename = filename
        self.font_index = font_index
        self.family_names = family_names
        self.weight = weight
        self.italic = italic
        self.exact_names = exact_names
        self.named_instance_coordinates = named_instance_coordinates

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
            if FontParser.is_file_truetype_collection(font_file):
                ttFonts.extend(TTCollection(font_path).fonts)
            elif FontParser.is_file_truetype(font_file) or FontParser.is_file_opentype(
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

                # If is Variable Font, else "normal" font
                if FontParser.is_valid_variable_font(ttFont):
                    fonts.extend(
                        Font._open_variable_font(ttFont, font_path, font_index)
                    )
                else:
                    try:
                        font = Font._open_normal_font(ttFont, font_path, font_index)
                    except InvalidFontException as e:
                        _logger.info(f"{e}. The font {font_path} will be ignored.")
                        continue

                    fonts.append(font)

        except Exception:
            _logger.error(
                f'An unknown error occurred while reading the font "{font_path}"{os.linesep}Please open an issue on github, share the font and the following error message:'
            )
            raise
        return fonts

    @classmethod
    def _open_normal_font(
        cls, ttFont: TTFont, font_path: str, font_index: int
    ) -> "Font":
        """
        Parameters:
            font (TTFont): An fontTools object
            font_path (str): Font path.
            font_index (int): Font index.
        Returns:
            An Font instance that represent the ttFont
        """

        is_truetype = FontParser.is_truetype(ttFont)

        families, fullnames = FontParser.get_font_family_fullname_property(
            ttFont["name"].names
        )

        # This is something like: https://github.com/libass/libass/blob/a2b39cde4ecb74d5e6fccab4a5f7d8ad52b2b1a4/libass/ass_fontselect.c#L303-L311
        if len(families) == 0:
            family_name = FontParser.get_name_by_id(
                NameID.FAMILY_NAME, ttFont["name"].names
            )

            if family_name:
                families.add(family_name)
            else:
                raise InvalidFontException(
                    "The font does not contain an valid family name"
                )

        if is_truetype:
            exact_names = fullnames
        else:
            exact_names = set()
            postscript_name = FontParser.get_font_postscript_property(
                font_path, font_index
            )
            if postscript_name is not None:
                exact_names.add(postscript_name)

        is_italic, weight = FontParser.get_font_italic_bold_property(
            ttFont, font_path, font_index
        )

        return cls(
            font_path,
            font_index,
            families,
            weight,
            is_italic,
            exact_names,
        )

    @classmethod
    def _open_variable_font(
        cls, ttFont: TTFont, font_path: str, font_index: int
    ) -> List["Font"]:
        """
        Parameters:
            font (TTFont): An fontTools object
            font_path (str): Font path.
            font_index (int): Font index.
        Returns:
            An list of Font instance that represent the ttFont.
        """
        fonts: List[Font] = []

        family_name_prefix = FontParser.get_var_font_family_prefix(ttFont)
        axis_values_coordinates: List[Tuple[Any, Dict[str, float]]] = []

        for instance in ttFont["fvar"].instances:
            families = set()
            fullnames = set()

            axis_value_table = FontParser.get_axis_value_from_coordinates(
                ttFont, instance.coordinates
            )

            instance_coordinates = instance.coordinates
            for axis_value_coordinates in axis_values_coordinates:
                if axis_value_coordinates[0] == axis_value_table:
                    instance_coordinates = axis_value_coordinates[1]
                    break
            axis_values_coordinates.append((axis_value_table, instance.coordinates))

            (
                family_name,
                full_name,
                weight,
                is_italic,
            ) = FontParser.get_axis_value_table_property(
                ttFont, axis_value_table, family_name_prefix
            )

            families.add(family_name)
            fullnames.add(full_name)

            font = cls(
                font_path,
                font_index,
                families,
                int(weight),
                is_italic,
                fullnames,
                instance_coordinates,
            )
            fonts.append(font)

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

    @property
    def is_var(self):
        return len(self.named_instance_coordinates) > 0

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
                self.filename,
                self.font_index,
                tuple(self.family_names),
                self.italic,
                self.weight,
                tuple(self.exact_names),
            )
        )

    def __repr__(self):
        return f'Filename: "{self.filename}" Family_names: "{self.family_names}", Weight: "{self.weight}", Italic: "{self.italic}, Exact_names: "{self.exact_names}", Named_instance_coordinates: "{self.named_instance_coordinates}"'

    def get_missing_glyphs(
        self,
        text: Sequence[str],
        support_only_ascii_char_for_symbol_font: bool = False
    ) -> Set[str]:
        """
        Parameters:
            text (Sequence[str]): Text
            support_only_ascii_char_for_symbol_font (bool):
                Libass only support ascii character for symbol cmap, but VSFilter can support more character.
                    If you wish to use libass, we recommand you to set this param to True.
                    If you wish to use VSFilter, we recommand you to set this param to False.
                For more detail, see the issue: https://github.com/libass/libass/issues/319
        Returns:
            A set of all the character that the font cannot display.
        """

        char_not_found: Set[str] = set()

        library = FT_Library()
        face = FT_Face()

        error = FT_Init_FreeType(byref(library))
        if error: raise FT_Exception(error)

        # We cannot use FT_New_Face due to this issue: https://github.com/rougier/freetype-py/issues/157
        with open(self.filename, mode="rb") as f:
            filebody = f.read()
        error = FT_New_Memory_Face(library, filebody, len(filebody), self.font_index, byref(face))
        if error: raise FT_Exception(error)

        supported_charmaps = [face.contents.charmaps[i] for i in range(face.contents.num_charmaps) if FT_Get_CMap_Format(face.contents.charmaps[i]) != -1 and face.contents.charmaps[i].contents.platform_id == 3]

        # GDI seems to take apple cmap if there isn't any microsoft cmap: https://github.com/libass/libass/issues/679
        if len(supported_charmaps) == 0:
            supported_charmaps = [face.contents.charmaps[i] for i in range(face.contents.num_charmaps) if FT_Get_CMap_Format(face.contents.charmaps[i]) != -1 and face.contents.charmaps[i].contents.platform_id == 1 and face.contents.charmaps[i].contents.encoding_id == 0]

        for char in text:
            char_found = False

            for charmap in supported_charmaps:
                error = FT_Set_Charmap(face, charmap)
                if error: raise FT_Exception(error)

                platform_id = charmap.contents.platform_id
                encoding_id = charmap.contents.encoding_id

                cmap_encoding = FontParser.get_cmap_encoding(platform_id, encoding_id)

                # cmap not supported 
                if cmap_encoding is None:
                    continue

                if cmap_encoding == "unicode":
                    codepoint = ord(char)
                else:
                    if cmap_encoding == "unknown":
                        if platform_id == 3 and encoding_id == 0:
                            if support_only_ascii_char_for_symbol_font and not char.isascii():
                                continue
                            cmap_encoding = FontParser.get_symbol_cmap_encoding(face)

                            if cmap_encoding is None:
                                # Fallback if guess fails
                                cmap_encoding = "cp1252"
                        else:
                            # cmap not supported 
                            continue

                    try:
                        codepoint = int.from_bytes(char.encode(cmap_encoding), "big")
                    except UnicodeEncodeError:
                        continue

                # GDI/Libass modify the codepoint for microsoft symbol cmap: https://github.com/libass/libass/blob/04a208d5d200360d2ac75f8f6cfc43dd58dd9225/libass/ass_font.c#L249-L250
                if platform_id == 3 and encoding_id == 0:
                    codepoint = 0xF000 | codepoint

                index = FT_Get_Char_Index(face, codepoint)

                if index:
                    char_found = True
                    break

            if not char_found:
                char_not_found.add(char)

        FT_Done_Face(face)
        FT_Done_FreeType(library)

        return char_not_found
