from __future__ import annotations

class AssStyle:
    """
    AssStyle is an instance that does NOT only represent "[V4+ Styles]" section of an .ass script.
    It also consider the tags \\r, \\i, \\b and \\fn
    """

    __fontname: str
    weight: int  # a.k.a bold
    italic: bool

    def __init__(
        self: AssStyle,
        fontname: str,
        weight: int,
        italic: bool,
    ):
        self.fontname = fontname
        self.weight = weight
        self.italic = italic


    @property
    def fontname(self: AssStyle):
        return self.__fontname

    @fontname.setter
    def fontname(self: AssStyle, value: str):
        self.__fontname = AssStyle.strip_fontname(value)


    def __eq__(self: AssStyle, other: AssStyle):
        return (self.fontname.lower(), self.weight, self.italic) == (
            other.fontname.lower(),
            other.weight,
            other.italic,
        )


    def __hash__(self: AssStyle):
        return hash((self.fontname.lower(), self.weight, self.italic))


    def __repr__(self: AssStyle):
        return f'{self.__class__.__name__}(Font name="{self.fontname}", Weight="{self.weight}", Italic="{self.italic}")'


    @staticmethod
    def strip_fontname(font_name: str) -> str:
        """
        Inpired by:
            - https://github.com/libass/libass/blob/a2b39cde4ecb74d5e6fccab4a5f7d8ad52b2b1a4/libass/ass_parse.c#L101

        Parameters:
            font_name (str): The font name.
        Returns:
            The font without an @ at the beginning
        """
        if font_name.startswith("@"):
            return font_name[1:]
        else:
            return font_name