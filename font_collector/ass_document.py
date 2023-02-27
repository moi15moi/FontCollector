import os
from .ass_style import AssStyle
from .usage_data import UsageData
from ass import parse_file, parse_string, Dialogue, Document
from ass_tag_analyzer import (
    AssInvalidTagBold,
    AssInvalidTagFontName,
    AssInvalidTagItalic,
    AssInvalidTagResetStyle,
    AssInvalidTagWrapStyle,
    AssItem,
    AssTagBold,
    AssTagFontName,
    AssTagItalic,
    AssTagResetStyle,
    AssTagWrapStyle,
    AssText,
    AssValidTagAnimation,
    AssValidTagBold,
    AssValidTagFontName,
    AssValidTagItalic,
    AssValidTagResetStyle,
    AssValidTagWrapStyle,
    parse_line,
    WrapStyle,
)
from typing import Dict, List


class AssDocument:

    subtitle: Document

    def __init__(self, subtitle: Document):
        self.subtitle = subtitle

    @classmethod
    def from_string(cls, file_text: str):
        return cls(parse_string(file_text))

    @classmethod
    def from_file(cls, filename: str, encoding: str = "utf_8_sig"):
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"The file {filename} is not reachable")

        with open(filename, encoding=encoding) as file:
            subtitle = parse_file(file)

        return cls(subtitle)

    def _set_used_styles(
        self,
        used_styles: Dict[AssStyle, UsageData],
        tags: List[AssItem],
        line_index: int,
        sub_styles: Dict[str, AssStyle],
        original_line_style: AssStyle,
        line_style: AssStyle,
        current_style: AssStyle,
        current_wrap_style: WrapStyle,
    ) -> None:
        """
        Parameters:
            used_styles (Dict[AssStyle, UsageData]): This variable will be modified
            tags (List[AssItem]): List of all tags
            line_index (int): Position of the line in the subtitle
            sub_styles (Dict[str, AssStyle]): Dict of the [V4+ Styles] sections
            original_line_style (AssStyle): Style of the line
            line_style (AssStyle): Style of the line. In general, it will be equal to original_line_style except it there is an \rXXX
            current_style (AssStyle): Real style of the text. It exist since \fn, \b, \i can override the line_style.
            current_wrap_style (WrapStyle): Since \q can override the subtitle WrapStyle, we need it.
        """

        for tag in tags:
            if isinstance(tag, AssTagResetStyle):
                if isinstance(tag, AssValidTagResetStyle):
                    style = sub_styles.get(tag.style, original_line_style)

                    # Copy the style
                    line_style = AssStyle(style.fontname, style.weight, style.italic)
                    current_style = AssStyle(style.fontname, style.weight, style.italic)
                elif isinstance(tag, AssInvalidTagResetStyle):
                    # Copy the original_line_style
                    line_style = AssStyle(
                        original_line_style.fontname,
                        original_line_style.weight,
                        original_line_style.italic,
                    )
                    current_style = AssStyle(
                        original_line_style.fontname,
                        original_line_style.weight,
                        original_line_style.italic,
                    )

            elif isinstance(tag, AssTagBold):
                if isinstance(tag, AssValidTagBold):
                    current_style.weight = tag.weight
                elif isinstance(tag, AssInvalidTagBold):
                    current_style.weight = line_style.weight

            elif isinstance(tag, AssTagItalic):
                if isinstance(tag, AssValidTagItalic):
                    current_style.italic = tag.enabled
                elif isinstance(tag, AssInvalidTagItalic):
                    current_style.italic = line_style.italic

            elif isinstance(tag, AssTagFontName):
                if isinstance(tag, AssValidTagFontName):
                    current_style.fontname = tag.name

                elif isinstance(tag, AssInvalidTagFontName):
                    current_style.fontname = line_style.fontname

            elif isinstance(tag, AssTagWrapStyle):
                if isinstance(tag, AssValidTagWrapStyle):
                    current_wrap_style = tag.style
                elif isinstance(tag, AssInvalidTagWrapStyle):
                    current_wrap_style = WrapStyle(self.subtitle.wrap_style)

            elif isinstance(tag, AssValidTagAnimation):
                self._set_used_styles(
                    used_styles,
                    tag.tags,
                    line_index,
                    sub_styles,
                    original_line_style,
                    line_style,
                    current_style,
                    current_wrap_style,
                )

            elif isinstance(tag, AssText):
                # Inspired by
                #     - https://github.com/libass/libass/blob/a2b39cde4ecb74d5e6fccab4a5f7d8ad52b2b1a4/libass/ass_parse.c#L1039-L1075
                #     - Aegisub FontCollector ignore \n: https://github.com/arch1t3cht/Aegisub/blob/fad362ec2e2975d8e37893c6dfb3a39452e71d23/src/font_file_lister.cpp#L118-L120
                text = tag.text.replace("\t", " ")
                if current_wrap_style == WrapStyle.NO_WORD:
                    text = text.replace("\\n", "")
                else:
                    text = text.replace("\\n", " ")
                text = text.replace("\\N", "")
                # Libass use latin space to render NBSP: https://github.com/libass/libass/blob/a2b39cde4ecb74d5e6fccab4a5f7d8ad52b2b1a4/libass/ass_font.c#L573-L574
                text = text.replace("\\h", " ")
                text = text.replace("\u00A0", " ")

                # Update or create the usage_data
                usage_data = used_styles.get(current_style, None)
                if usage_data is None:
                    usage_data = UsageData(set(text), set([line_index]))
                    used_styles[current_style] = usage_data
                else:
                    usage_data.characters_used.update(set(text))
                    usage_data.lines.add(line_index)

                # We need to make an copy of the style since current_style can be modified
                current_style = AssStyle(
                    current_style.fontname, current_style.weight, current_style.italic
                )

    def get_used_style(self) -> Dict[AssStyle, UsageData]:
        """
        Returns:
            An dictionnary which contain all the used AssStyle and it's UsageData.
        """
        used_styles: Dict[AssStyle, UsageData] = {}

        # VSFilter trim:
        #   - *: https://sourceforge.net/p/guliverkli2/code/HEAD/tree/src/subtitles/STS.cpp#l1447
        #   - tabulation and space : https://sourceforge.net/p/guliverkli2/code/HEAD/tree/src/subtitles/STS.cpp#l1172
        sub_styles: Dict[str, AssStyle] = {
            style.name.lstrip("\t ").lstrip("*"): AssStyle(
                style.fontname.lstrip("\t "), 700 if style.bold else 400, style.italic
            )
            for style in self.subtitle.styles
        }

        try:
            sub_wrap_style = WrapStyle(self.subtitle.wrap_style)
        except KeyError:
            sub_wrap_style = WrapStyle.SMART_TOP

        for i, line in enumerate(self.subtitle.events):
            if isinstance(line, Dialogue):
                try:
                    original_line_style = sub_styles[line.style]
                except KeyError:
                    raise ValueError(
                        f'Error: Unknown style "{line.style}" on line {i+1}. You need to correct the .ass file.'
                    )

                tags = parse_line(line.text)

                # Copy the original_line_style
                line_style = AssStyle(
                    original_line_style.fontname,
                    original_line_style.weight,
                    original_line_style.italic,
                )
                current_style = AssStyle(
                    original_line_style.fontname,
                    original_line_style.weight,
                    original_line_style.italic,
                )

                self._set_used_styles(
                    used_styles,
                    tags,
                    i + 1,
                    sub_styles,
                    original_line_style,
                    line_style,
                    current_style,
                    sub_wrap_style,
                )

        return used_styles
