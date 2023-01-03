from .font import Font


class FontResult:

    font: Font
    mismatch_bold: bool
    mismatch_italic: bool

    def __init__(
        self,
        font: Font,
        mismatch_bold: bool,
        mismatch_italic: bool,
    ):
        self.font = font
        self.mismatch_bold = mismatch_bold
        self.mismatch_italic = mismatch_italic

    def __repr__(self):
        return f'font: "{self.font}", mismatch_bold: "{self.mismatch_bold}", mismatch_italic: "{self.mismatch_italic}"'
