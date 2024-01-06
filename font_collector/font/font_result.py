from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .abc_font_face import ABCFontFace

__all__ = ["FontResult"]

class FontResult:

    def __init__(
        self: FontResult,
        font_face: ABCFontFace,
        mismatch_bold: bool,
        need_faux_bold: bool,
        mismatch_italic: bool,
    ) -> None:
        self.font_face = font_face
        self.mismatch_bold = mismatch_bold
        self.need_faux_bold = need_faux_bold
        self.mismatch_italic = mismatch_italic


    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FontResult):
            return False
        return (self.font_face, self.mismatch_bold, self.need_faux_bold, self.mismatch_italic) == (
            other.font_face, other.mismatch_bold, other.need_faux_bold, other.mismatch_italic
        )


    def __hash__(self) -> int:
        return hash(
            (
                self.font_face,
                self.mismatch_bold,
                self.need_faux_bold,
                self.mismatch_italic,
            )
        )


    def __repr__(self: FontResult) -> str:
        return f'{self.__class__.__name__}(Font face="{self.font_face}", Mismatch bold="{self.mismatch_bold}", Need faux bold="{self.need_faux_bold}", Mismatch italic="{self.mismatch_italic}")'