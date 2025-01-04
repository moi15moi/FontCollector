from __future__ import annotations
from ..exceptions import InvalidNormalFontFaceException
from .abc_font_face import ABCFontFace
from .font_type import FontType
from .name import Name
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from . import FontFile


__all__ = ["NormalFontFace"]

class NormalFontFace(ABCFontFace):
    """Represents a normal font face of a font file.
    A normal font face can also be called a static face.
    The vast majority of font are this kind of type.

    For the list of Attributes, see the doc of: ABCFontFace
    """

    def __init__(
        self,
        font_index: int,
        family_names: list[Name],
        exact_names: list[Name],
        weight: int,
        is_italic: bool,
        is_glyph_emboldened: bool,
        font_type: FontType,
    ) -> None:
        if len(family_names) == 0:
            raise InvalidNormalFontFaceException("A font face needs to contain at least 1 family name.")

        self.__font_index = font_index
        self.__family_names = family_names
        self.__exact_names = exact_names
        self.__weight = weight
        self.__is_italic = is_italic
        self.__is_glyph_emboldened = is_glyph_emboldened
        self.__font_type = font_type
        self.__font_file = None

    @property
    def font_index(self) -> int:
        return self.__font_index

    @property
    def family_names(self) -> list[Name]:
        return self.__family_names

    @property
    def exact_names(self) -> list[Name]:
        # if the font is a TrueType, it will be the "full_name". if the font is a OpenType, it will be the "postscript name"
        return self.__exact_names

    @property
    def weight(self) -> int:
        return self.__weight

    @property
    def is_italic(self) -> bool:
        return self.__is_italic

    @property
    def is_glyph_emboldened(self) -> bool:
        return self.__is_glyph_emboldened

    @property
    def font_type(self) -> FontType:
        return self.__font_type

    @property
    def font_file(self) -> Optional[FontFile]:
        return self.__font_file

    def link_face_to_a_font_file(self, value: FontFile) -> None:
        # Since there is a circular reference between FontFile and this class, we need to be able to set the value
        self.__font_file = value


    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NormalFontFace):
            return False
        return (self.font_index, self.family_names, self.exact_names, self.weight, self.is_italic, self.is_glyph_emboldened, self.font_type) == (
            other.font_index, other.family_names, other.exact_names, other.weight, other.is_italic, other.is_glyph_emboldened, other.font_type
        )


    def __hash__(self) -> int:
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


    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(Font index="{self.font_index}", Family names="{self.family_names}", Exact names="{self.exact_names}", Weight="{self.weight}", Italic="{self.is_italic}", Glyph emboldened="{self.is_glyph_emboldened}", Font type="{self.font_type.name}")'
