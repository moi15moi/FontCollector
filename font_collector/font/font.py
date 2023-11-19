from __future__ import annotations
from .abc_font import ABCFont, FontType
from ..exceptions import InvalidLanguageCode
from .name import Name
from langcodes import Language, tag_is_valid
from os import PathLike
from typing import List, Set


class Font(ABCFont):

    def __init__(
        self: Font,
        filename: PathLike[str],
        font_index: int,
        family_names: List[Name],
        exact_names: List[Name],
        weight: int,
        is_italic: bool,
        is_glyph_emboldened: bool,
        font_type: FontType
    ) -> Font:
        self.filename = filename
        self.font_index = font_index
        self.family_names = family_names
        self.exact_names = exact_names
        self.weight = weight
        self.is_italic = is_italic
        self.is_glyph_emboldened = is_glyph_emboldened
        self.font_type = font_type

    
    def __eq__(self: Font, other: Font) -> bool:
        return (self.filename, self.font_index, self.family_names, self.exact_names, self.weight, self.is_italic, self.is_glyph_emboldened, self.font_type) == (
            other.filename, other.font_index, other.family_names, other.exact_names, other.weight, other.is_italic, other.is_glyph_emboldened, other.font_type
        )


    def __hash__(self: Font) -> int:
        return hash(
            (
                self.filename,
                self.font_index,
                tuple(self.family_names),
                tuple(self.exact_names),
                self.weight,
                self.is_italic,
                self.is_glyph_emboldened,
                self.font_type,
            )
        )


    def __repr__(self: Font) -> str:
        return f'Font(Filename="{self.filename}", Font index="{self.font_index}", Family_names="{self.family_names}", Exact_names="{self.exact_names}", Weight="{self.weight}", Italic="{self.is_italic}", Glyph emboldened="{self.is_glyph_emboldened}", Font type="{self.font_type.name}")'
