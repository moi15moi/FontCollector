from __future__ import annotations

from .abc_font_face import ABCFontFace

__all__ = ["FontResult"]

class FontResult:
    """Represents the result of font analysis which include mismatch information
    between the ABCFontFace and a AssStyle

    Attributes:
        font_face: The font face object.
        mismatch_bold: Indicates if there is a mismatch in bold style.
            Unlike faux_bold, it occurs when the weight is too different with
                the AssStyle weight.
            For example, the AssStyle weight could be 400, but the ABCFontFace could be 700,
                so there wouldn't need faux bold, but there is a weight mismatch.
        need_faux_bold: Indicates if faux bolding is needed.
        mismatch_italic: Indicates if there is a mismatch in italic style.
    """

    def __init__(
        self,
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


    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(Font face="{self.font_face}", Mismatch bold="{self.mismatch_bold}", Need faux bold="{self.need_faux_bold}", Mismatch italic="{self.mismatch_italic}")'
