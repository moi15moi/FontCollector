import os
from pathlib import Path

import pytest
from ass import Comment, Dialogue, Document, Style
from ass_tag_analyzer import WrapStyle

from font_collector import AssDocument, AssStyle, UsageData

dir_path = os.path.dirname(os.path.realpath(__file__))
test_ass_file_dir_path = os.path.join(os.path.dirname(dir_path), "file", "ass")

def test_get_style_used():
    path_ass = Path(os.path.join(test_ass_file_dir_path, "Style test.ass"))
    subtitle = AssDocument.from_file(path_ass)

    styles = subtitle.get_used_style()

    expected_results = {
        AssStyle("Sunny Spells", 700, True): UsageData(set("example"), {1}), # Multiple tag
        AssStyle("Akashi", 700, True): UsageData(set("Multiple \\t"), {2}), # Test Font Name with multiple \t
        AssStyle("Test multiple \\b Font", 100, False): UsageData(set("text"), {3}), # Test multiple \b
        AssStyle("Test multiple \\b Font", 200, False): UsageData(set("text"), {3}), # Test multiple \b
        AssStyle("Font Test 1", 400, False): UsageData(set("text"), {4}), # Test multiple \fn
        AssStyle("Font Test 2", 400, False): UsageData(set("text"), {4}), # Test multiple \fn
        AssStyle("Reset Style 1 Font", 400, False): UsageData(set("text"), {5}), # Test multiple \r
        AssStyle("Reset Style 2 Font", 400, False): UsageData(set("text"), {5}), # Test multiple \r
        AssStyle("Test multiple \\i Font", 400, False): UsageData(set("text"), {6}), # Test multiple \i
        AssStyle("Test multiple \\i Font", 400, True): UsageData(set("text"), {6}), # Test multiple \i
        AssStyle("Test invalid \\b Font", 400, False): UsageData(set("Test"), {7}), # Test invalid \b
        AssStyle("Test invalid \\fn Font", 400, False): UsageData(set("Test"), {8}), # Test invalid \fn
        AssStyle("Test invalid \\r Style name Font", 400, False): UsageData(set("Don't match with style"), {9}), # Test invalid \r Style name
        AssStyle("Test invalid \\r Font", 400, False): UsageData(set("Test"), {10}), # Test invalid \r
        AssStyle("Test invalid \\i Font", 400, True): UsageData(set("Test"), {11}), # Test invalid \i
    }

    assert styles == expected_results


def test_get_style_used_with_and_without_collect_draw_fonts():
    path_ass = Path(os.path.join(test_ass_file_dir_path, "Collect Draw Style test.ass"))
    subtitle = AssDocument.from_file(path_ass)

    styles = subtitle.get_used_style()
    expected_results = {
        AssStyle("Jester", 700, False): UsageData(set("Test"), {1}),
    }
    assert styles == expected_results

    styles = subtitle.get_used_style(True)
    expected_results = {
        AssStyle("Jester", 700, False): UsageData(set("Test"), {1}),
        AssStyle("TestGmail", 700, False): UsageData(set(), {2}),
    }
    assert styles == expected_results


def test_get_style_used_with_invalid_style_name_and_empty_line():
    path_ass = Path(os.path.join(test_ass_file_dir_path, "Empty line with invalid style.ass"))
    subtitle = AssDocument.from_file(path_ass)

    styles = subtitle.get_used_style()
    expected_results = {}
    assert styles == expected_results


def test_get_style_used_with_invalid_style_name_and_non_empty_line():
    path_ass = Path(os.path.join(test_ass_file_dir_path, "Non-empty line with invalid style.ass"))
    subtitle = AssDocument.from_file(path_ass)

    with pytest.raises(ValueError) as exc_info:
        subtitle.get_used_style()
    assert str(exc_info.value) == f'Error: Unknown style "Test" on line 1. You need to correct the .ass file.'


def test_get_style_used_with_wrap_tag():
    path_ass = Path(os.path.join(test_ass_file_dir_path, "WrapStyle.ass"))
    subtitle = AssDocument.from_file(path_ass)

    styles = subtitle.get_used_style()
    expected_results = {AssStyle("Verdana", 400, False): UsageData(set("Test"), {1}),}
    assert styles == expected_results

    subtitle.subtitle.wrap_style = 3
    styles = subtitle.get_used_style()
    expected_results = {AssStyle("Verdana", 400, False): UsageData(set("Test "), {1}),}
    assert styles == expected_results


def test_get_style_used_usage_data():
    path_ass = Path(os.path.join(test_ass_file_dir_path, "Usage Data Test.ass"))
    subtitle = AssDocument.from_file(path_ass)

    styles = subtitle.get_used_style(collect_draw_fonts=True)
    expected_results = {
        AssStyle("Verdana", 400, False): UsageData(set("123456"), {1, 3}),
        AssStyle("Arial", 400, False): UsageData(set(""), {2, 4}),
     }
    assert styles == expected_results


def test_get_style_used_empty_line_style_name():
    path_ass = Path(os.path.join(test_ass_file_dir_path, "Empty line style name.ass"))
    subtitle = AssDocument.from_file(path_ass)

    styles = subtitle.get_used_style()
    expected_results = {
        AssStyle("Verdana", 700, False): UsageData(set("Test"), {1}),
    }
    assert styles == expected_results


def test_get_style_used_2_duplicate_style_name():
    path_ass = Path(os.path.join(test_ass_file_dir_path, "2 duplicate style name.ass"))
    subtitle = AssDocument.from_file(path_ass)

    styles = subtitle.get_used_style()
    expected_results = {
        AssStyle("Jester", 700, False): UsageData(set("Jester"), {1}),
    }
    assert styles == expected_results


def test_get_style_used_3_duplicate_style_name():
    path_ass = Path(os.path.join(test_ass_file_dir_path, "3 duplicate style name.ass"))
    subtitle = AssDocument.from_file(path_ass)

    styles = subtitle.get_used_style()
    expected_results = {
        AssStyle("Jester", 700, False): UsageData(set("Jester"), {1}),
    }
    assert styles == expected_results


def test_get_style_used_2_duplicate_style_name_with_number():
    path_ass = Path(os.path.join(test_ass_file_dir_path, "2 duplicate style name with number.ass"))
    subtitle = AssDocument.from_file(path_ass)

    styles = subtitle.get_used_style()
    expected_results = {
        AssStyle("Raleway", 700, False): UsageData(set("Raleway"), {1}),
    }
    assert styles == expected_results


def test_get_sub_wrap_style():
    ass = Document()
    subtitle = AssDocument(ass)

    assert subtitle.get_sub_wrap_style() == WrapStyle.SMART_TOP


def test_get_nbr_style():
    ass = Document()
    subtitle = AssDocument(ass)
    assert subtitle.get_nbr_style() == 0

    ass.styles = [Style()]
    assert subtitle.get_nbr_style() == 1


def test_get_style():
    ass = Document()
    subtitle = AssDocument(ass)

    with pytest.raises(ValueError) as exc_info:
        subtitle.get_style(0)
    assert str(exc_info.value) == "There isn't any style at the index 0. There is only 0 style(s)"

    ass.styles = [Style(Name="Style Name", Fontname="Fontname", Bold=False, Italic=True)]
    assert subtitle.get_style(0) == ("Style Name", "Fontname", False, True)


def test_get_sub_styles():
    ass = Document()
    subtitle = AssDocument(ass)

    ass.styles = [Style(Name=" \t * Test", Fontname="\t@Fontname", Bold=False, Italic=True)]

    expected_results = {
        " Test" : AssStyle("Fontname", 400, True)
    }

    assert subtitle.get_sub_styles() == expected_results


def test_get_nbr_line():
    ass = Document()
    subtitle = AssDocument(ass)
    assert subtitle.get_nbr_line() == 0

    ass.events = [Dialogue()]
    assert subtitle.get_nbr_line() == 1


def test_get_line_style_name():
    ass = Document()
    subtitle = AssDocument(ass)

    with pytest.raises(ValueError) as exc_info:
        subtitle.get_line_style_name(0)
    assert str(exc_info.value) == "There isn't any line at the index 0. There is only 0 line(s)"

    ass.events = [Dialogue(Style="Example")]
    assert subtitle.get_line_style_name(0) == "Example"


def test_get_line_text():
    ass = Document()
    subtitle = AssDocument(ass)

    with pytest.raises(ValueError) as exc_info:
        subtitle.get_line_text(0)
    assert str(exc_info.value) == "There isn't any line at the index 0. There is only 0 line(s)"

    ass.events = [Dialogue(Text="Example")]
    assert subtitle.get_line_text(0) == "Example"


def test_is_line_dialogue():
    ass = Document()
    subtitle = AssDocument(ass)

    with pytest.raises(ValueError) as exc_info:
        subtitle.is_line_dialogue(0)
    assert str(exc_info.value) == "There isn't any line at the index 0. There is only 0 line(s)"

    ass.events = [Dialogue(), Comment()]
    assert subtitle.is_line_dialogue(0) == True
    assert subtitle.is_line_dialogue(1) == False


def test_from_string():
    ass_text = """
    [Script Info]
    ; Script generated by Aegisub 9214, Daydream Cafe Edition [Shinon]
    ; http://www.aegisub.org/
    Title: Default Aegisub file
    ScriptType: v4.00+
    WrapStyle: 0
    ScaledBorderAndShadow: yes
    YCbCr Matrix: None
    PlayResX: 640
    PlayResY: 480

    [V4+ Styles]
    Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
    Style: Default,Verdana,35,&H00FFFFFF,&H000000FF,&H002C2C2C,&H00000000,-1,0,0,0,100,100,0,0,1,2.5,0,2,0,0,72,1

    [Events]
    Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
    Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,{\\fnJester}Test
    """
    subtitle = AssDocument.from_string(ass_text)
    assert subtitle.is_line_dialogue(0) == True
    assert subtitle.get_line_text(0) == "{\\fnJester}Test"
    assert subtitle.get_line_style_name(0) == "Default"


def test_from_file():
    filename = Path(os.path.join(test_ass_file_dir_path, "Ass file that doesn't exist.ass"))

    with pytest.raises(FileNotFoundError) as exc_info:
        AssDocument.from_file(filename)
    assert str(exc_info.value) == f"The file {filename} is not reachable"

    filename = Path(os.path.join(test_ass_file_dir_path, "Style test.ass"))
    subtitle = AssDocument.from_file(filename)
    assert subtitle.is_line_dialogue(6) == True
    assert subtitle.get_line_text(6) == "{\\b900\\b}Test"
    assert subtitle.get_line_style_name(6) == "Test invalid \\b"
