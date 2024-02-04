from __future__ import annotations

__all__ = ["AssStyle"]

class AssStyle:
    """
    AssStyle is an instance that does NOT only represent "[V4+ Styles]" section of an .ass script.
    It also consider the tags \\r, \\i, \\b and \\fn

    Attributes:
        fontname: The fontname used. Ex: "Arial".
        weight: The weight requested.
                For more information, see: https://learn.microsoft.com/en-us/typography/opentype/spec/os2#usweightclass
        italic: True if italic, otherwhise, false.
    """

    __fontname: str
    weight: int  # a.k.a bold
    italic: bool

    def __init__(
        self,
        fontname: str,
        weight: int,
        italic: bool,
    ) -> None:
        self.fontname = fontname
        self.weight = weight
        self.italic = italic


    @property
    def fontname(self) -> str:
        return self.__fontname

    @fontname.setter
    def fontname(self, value: str) -> None:
        self.__fontname = AssStyle.strip_fontname(value)


    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AssStyle):
            return False
        return (self.fontname.lower(), self.weight, self.italic) == (
            other.fontname.lower(),
            other.weight,
            other.italic,
        )


    def __hash__(self) -> int:
        return hash((self.fontname.lower(), self.weight, self.italic))


    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(Font name="{self.fontname}", Weight="{self.weight}", Italic="{self.italic}")'


    @staticmethod
    def strip_fontname(font_name: str) -> str:
        """
        Inpired by:
            - https://github.com/libass/libass/blob/a2b39cde4ecb74d5e6fccab4a5f7d8ad52b2b1a4/libass/ass_parse.c#L101

        Args:
            font_name: The font name.
        Returns:
            The font without an @ at the beginning
        """
        if font_name.startswith("@"):
            return font_name[1:]
        else:
            return font_name
