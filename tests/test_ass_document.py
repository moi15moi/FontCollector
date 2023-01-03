import os
from font_collector import AssDocument, AssStyle, UsageData

# Get ass path used for tests
dir_path = os.path.dirname(os.path.realpath(__file__))
path_ass = os.path.join(dir_path, "ass", "Untitled.ass")
path_font_directory = os.path.join(dir_path, "fonts")

subtitle = AssDocument.from_file(path_ass)


def test_get_style_used():
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
