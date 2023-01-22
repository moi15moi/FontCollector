import os
from font_collector import AssDocument, Helpers, FontLoader

# Get ass path used for tests
dir_path = os.path.dirname(os.path.realpath(__file__))
path_ass = os.path.join(dir_path, "ass", "Bold italic test.ass")

subtitle = AssDocument.from_file(path_ass)


def test_get_used_font_by_style():
    styles = subtitle.get_used_style()
    styles = list(styles.keys())

    assert len(styles) == 1

    style = styles[0]
    font_collection = FontLoader(
        [os.path.join(dir_path, "fonts", "Raleway")], False
    ).fonts

    font_result = Helpers.get_used_font_by_style(font_collection, style)

    # VSFilter prefer to match to the weight then the italic.
    # If it would have prefer to match the italic, the weight would be 700 and italic would be true.
    assert font_result.font.weight == 900
    assert font_result.font.italic == False

test_get_used_font_by_style()