from __future__ import annotations
from .abc_font_face import ABCFontFace


class FontResult:

    font: ABCFontFace
    mismatch_bold: bool
    mismatch_italic: bool

    def __init__(
        self: FontResult,
        font: ABCFontFace,
        mismatch_bold: bool,
        need_faux_bold: bool,
        mismatch_italic: bool,
    ) -> None:
        self.font = font
        self.mismatch_bold = mismatch_bold
        self.need_faux_bold = need_faux_bold
        self.mismatch_italic = mismatch_italic


    def __repr__(self):
        return f'FontResult(Font="{self.font}", Mismatch bold="{self.mismatch_bold}", Need faux bold="{self.need_faux_bold}", Mismatch italic="{self.mismatch_italic}")'