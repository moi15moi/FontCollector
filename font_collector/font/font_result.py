from __future__ import annotations
from .abc_font_face import ABCFontFace


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


    def __repr__(self):
        return f'{self.__class__.__name__}(Font face="{self.font_face}", Mismatch bold="{self.mismatch_bold}", Need faux bold="{self.need_faux_bold}", Mismatch italic="{self.mismatch_italic}")'