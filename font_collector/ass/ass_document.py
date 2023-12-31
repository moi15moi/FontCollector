from __future__ import annotations
import os
from .abc_ass_document import ABCAssDocument
from ass import Dialogue, Document, parse_file, parse_string
from ass_tag_analyzer import WrapStyle
from typing import Optional, Tuple, Type


class AssDocument(ABCAssDocument):

    def __init__(self: AssDocument, subtitle: Document) -> None:
        self.subtitle = subtitle


    @classmethod
    def from_string(cls: Type[AssDocument], file_text: str) -> AssDocument:
        return cls(parse_string(file_text))


    @classmethod
    def from_file(cls: Type[AssDocument], filename: str, encoding: str = "utf_8_sig") -> AssDocument:
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"The file {filename} is not reachable")

        with open(filename, encoding=encoding) as file:
            subtitle = parse_file(file)

        return cls(subtitle)


    def _get_sub_wrap_style(self: AssDocument) -> Optional[WrapStyle]:
        try:
            sub_wrap_style = WrapStyle(self.subtitle.wrap_style)
        except KeyError:
            sub_wrap_style = None
        
        return sub_wrap_style


    def get_nbr_style(self: AssDocument) -> int:
        nbr_style = len(self.subtitle.styles)

        return nbr_style


    def _get_style(self: AssDocument, i: int) -> Tuple[str, str, bool, bool]:
        style_name = self.subtitle.styles[i].name
        font_name = self.subtitle.styles[i].fontname
        is_bold = self.subtitle.styles[i].bold
        is_italic = self.subtitle.styles[i].italic

        return style_name, font_name, is_bold, is_italic


    def get_nbr_line(self: AssDocument) -> int:
        nbr_line = len(self.subtitle.events)

        return nbr_line


    def _get_line_style_name(self: AssDocument, i: int) -> str:
        return self.subtitle.events[i].style


    def _get_line_text(self: AssDocument, i: int) -> str:
        return self.subtitle.events[i].text
    

    def _is_line_dialogue(self: AssDocument, i: int) -> bool:
        return isinstance(self.subtitle.events[i], Dialogue)