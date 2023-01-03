class AssStyle:
    """
    AssStyle is an instance that does not only represent "[V4+ Styles]" section of an .ass script.
    It also consider the tags \r, \i, \b and \fn
    """

    __fontname: str
    weight: int  # a.k.a bold
    italic: bool

    def __init__(
        self,
        fontname: str,
        weight: int,
        italic: bool,
    ):
        self.fontname = fontname
        self.weight = weight
        self.italic = italic

    @property
    def fontname(self):
        return self.__fontname

    @fontname.setter
    def fontname(self, value: str):
        self.__fontname = AssStyle.strip_fontname(value.lower())

    def __eq__(self, other: "AssStyle"):
        return (self.fontname, self.weight, self.italic) == (
            other.fontname,
            other.weight,
            other.italic,
        )

    def __hash__(self):
        return hash((self.fontname, self.weight, self.italic))

    def __repr__(self):
        return f'Fontname: "{self.fontname}", weight: "{self.weight}", italic: "{self.italic}"'

    @staticmethod
    def strip_fontname(fontName: str) -> str:
        """
        Inpired by:
            - https://github.com/libass/libass/blob/a2b39cde4ecb74d5e6fccab4a5f7d8ad52b2b1a4/libass/ass_parse.c#L101
            - https://github.com/TypesettingTools/Myaamori-Aegisub-Scripts/blob/f2a52ee38eeb60934175722fa9d7f2c2aae015c6/scripts/fontvalidator/fontvalidator.py#L33-L37

        Parameters:
            fontName (str): The font name.
        Returns:
            The font without an @ at the beginning
        """
        if fontName.startswith("@"):
            return fontName[1:]
        else:
            return fontName
