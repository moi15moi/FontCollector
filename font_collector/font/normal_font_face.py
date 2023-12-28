from __future__ import annotations
from ..exceptions import InvalidNormalFontFaceException
from .abc_font_face import ABCFontFace, FontType
from .name import Name
from langcodes import Language, tag_is_valid
from os import PathLike
from typing import List, TYPE_CHECKING


class NormalFontFace(ABCFontFace):

    def __init__(
        self: NormalFontFace,
        font_index: int,
        family_names: List[Name],
        exact_names: List[Name],
        weight: int,
        is_italic: bool,
        is_glyph_emboldened: bool,
        font_type: FontType,
    ) -> NormalFontFace:
        if len(family_names) == 0:
                raise InvalidNormalFontFaceException("The font does not contain an valid family name")

        self._font_index = font_index
        self._family_names = family_names
        self._exact_names = exact_names
        self._weight = weight
        self._is_italic = is_italic
        self._is_glyph_emboldened = is_glyph_emboldened
        self._font_type = font_type
        self._font_file = None
    
    def __eq__(self: NormalFontFace, other: NormalFontFace) -> bool:
        return (self.font_index, self.family_names, self.exact_names, self.weight, self.is_italic, self.is_glyph_emboldened, self.font_type) == (
            other.font_index, other.family_names, other.exact_names, other.weight, other.is_italic, other.is_glyph_emboldened, other.font_type
        )


    def __hash__(self: NormalFontFace) -> int:
        return hash(
            (
                self.font_index,
                tuple(self.family_names),
                tuple(self.exact_names),
                self.weight,
                self.is_italic,
                self.is_glyph_emboldened,
                self.font_type,
            )
        )


    def __repr__(self: NormalFontFace) -> str:
        return f'{self.__class__.__name__}(Font index="{self.font_index}", Family names="{self.family_names}", Exact names="{self.exact_names}", Weight="{self.weight}", Italic="{self.is_italic}", Glyph emboldened="{self.is_glyph_emboldened}", Font type="{self.font_type.name}")'
