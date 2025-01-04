from __future__ import annotations

from pathlib import Path
from typing import Optional

from ass import Dialogue, Document, parse_file, parse_string
from ass_tag_analyzer import WrapStyle

from .abc_ass_document import ABCAssDocument

__all__ = ["AssDocument"]

class AssDocument(ABCAssDocument):

    def __init__(self, subtitle: Document) -> None:
        self.subtitle = subtitle


    @classmethod
    def from_string(cls: type[AssDocument], file_text: str) -> AssDocument:
        return cls(parse_string(file_text))


    @classmethod
    def from_file(cls: type[AssDocument], filename: Path, encoding: str = "utf_8_sig") -> AssDocument:
        if not filename.is_file():
            raise FileNotFoundError(f"The file {filename} is not reachable")

        with open(filename, encoding=encoding) as file:
            subtitle = parse_file(file)

        return cls(subtitle)


    def _get_sub_wrap_style(self) -> Optional[WrapStyle]:
        try:
            sub_wrap_style = WrapStyle(self.subtitle.wrap_style)
        except KeyError:
            sub_wrap_style = None

        return sub_wrap_style


    def get_nbr_style(self) -> int:
        nbr_style = len(self.subtitle.styles)

        return nbr_style


    def _get_style(self, i: int) -> tuple[str, str, bool, bool]:
        style_name = self.subtitle.styles[i].name
        font_name = self.subtitle.styles[i].fontname
        is_bold = self.subtitle.styles[i].bold
        is_italic = self.subtitle.styles[i].italic

        return style_name, font_name, is_bold, is_italic


    def get_nbr_line(self) -> int:
        nbr_line = len(self.subtitle.events)
        return nbr_line


    def _get_line_style_name(self, i: int) -> str:
        style: str = self.subtitle.events[i].style
        return style


    def _get_line_text(self, i: int) -> str:
        text: str = self.subtitle.events[i].text
        return text


    def _is_line_dialogue(self, i: int) -> bool:
        return isinstance(self.subtitle.events[i], Dialogue)
