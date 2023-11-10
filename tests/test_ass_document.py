import os
from font_collector import AssDocument, AssStyle, UsageData

# Get ass path used for tests
dir_path = os.path.dirname(os.path.realpath(__file__))


def test_get_style_used():
    path_ass = os.path.join(dir_path, "ass", "Style test.ass")
    subtitle = AssDocument.from_file(path_ass)

    styles = subtitle.get_used_style()

    expected_results = {
        AssStyle("Sunny Spells", 700, True): UsageData(set("example"), {1}),
        AssStyle("Akashi", 700, True): UsageData(set("Multiple \\t"), {2}),
        AssStyle("Bodo Amat", 400, True): UsageData(set("Italic"), {3}),
        AssStyle("Bodo Amat", 400, False): UsageData(set("Regular"), {3}),
        AssStyle("Avenir LT 65 Medium", 400, False): UsageData(
            set("Don't match with style"), {4}
        ),
        AssStyle("Asap", 400, True): UsageData(set("\\r override"), {5}),
    }

    assert styles == expected_results


def test_get_style_used_with_and_without_collect_draw_fonts():
    path_ass = os.path.join(dir_path, "ass", "Collect Draw Style test.ass")
    subtitle = AssDocument.from_file(path_ass)

    styles = subtitle.get_used_style()
    expected_results = {
        AssStyle("Jester", 700, False): UsageData(set("Test"), {1}),
    }
    assert styles == expected_results

    styles = subtitle.get_used_style(True)
    expected_results = {
        AssStyle("Jester", 700, False): UsageData(set("Test"), {1}),
        AssStyle("testgmail", 700, False): UsageData(set(), {2}),
    }
    assert styles == expected_results


def test_get_style_used_empty_line_style_name():
    path_ass = os.path.join(dir_path, "ass", "Empty line style name.ass")
    subtitle = AssDocument.from_file(path_ass)

    styles = subtitle.get_used_style()
    expected_results = {
        AssStyle("Verdana", 700, False): UsageData(set("Test"), {1}),
    }
    assert styles == expected_results


def test_get_style_used_2_duplicate_style_name():
    path_ass = os.path.join(dir_path, "ass", "2 duplicate style name.ass")
    subtitle = AssDocument.from_file(path_ass)

    styles = subtitle.get_used_style()
    expected_results = {
        AssStyle("Jester", 700, False): UsageData(set("Jester"), {1}),
    }
    assert styles == expected_results


def test_get_style_used_3_duplicate_style_name():
    path_ass = os.path.join(dir_path, "ass", "3 duplicate style name.ass")
    subtitle = AssDocument.from_file(path_ass)

    styles = subtitle.get_used_style()
    expected_results = {
        AssStyle("Jester", 700, False): UsageData(set("Jester"), {1}),
    }
    assert styles == expected_results


def test_get_style_used_2_duplicate_style_name_with_number():
    path_ass = os.path.join(dir_path, "ass", "2 duplicate style name with number.ass")
    subtitle = AssDocument.from_file(path_ass)

    styles = subtitle.get_used_style()
    expected_results = {
        AssStyle("Raleway", 700, False): UsageData(set("Raleway"), {1}),
    }
    assert styles == expected_results