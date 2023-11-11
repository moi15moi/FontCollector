import os
from font_collector import FontLoader
from pathlib import Path

dir_path = os.path.dirname(os.path.realpath(__file__))


def test_load_additional_fonts():
    font_directory = os.path.join(dir_path, "fonts")

    fonts_result = FontLoader.load_additional_fonts([Path(font_directory)])
    result = list(set([font.filename for font in fonts_result]))
    expected_result = [
        os.path.join(font_directory, "Asap-VariableFont_wdth,wght.ttf"),
        os.path.join(font_directory, "Cabin VF Beta Regular.ttf"),
        os.path.join(font_directory, "font_cmap_encoding_0.ttf"),
        os.path.join(font_directory, "font_cmap_encoding_1.ttf"),
        os.path.join(font_directory, "font_cmap_encoding_2.TTF"),
        os.path.join(font_directory, "font_mac.TTF"),
        os.path.join(font_directory, "font_without axis_value.ttf")
    ]

    assert sorted(result) == sorted(expected_result)


    fonts_result = FontLoader.load_additional_fonts([Path(font_directory)], scan_subdirs=True)
    result = list(set([font.filename for font in fonts_result]))
    expected_result.extend([
        os.path.join(font_directory, "Raleway", "Raleway-Black.ttf"),
        os.path.join(font_directory, "Raleway", "Raleway-Bold.ttf"),
        os.path.join(font_directory, "Raleway", "Raleway-BoldItalic.ttf"),
        os.path.join(font_directory, "Raleway", "Raleway-ExtraBold.ttf"),
        os.path.join(font_directory, "Raleway", "Raleway-ExtraLight.ttf"),
        os.path.join(font_directory, "Raleway", "Raleway-Italic.ttf"),
        os.path.join(font_directory, "Raleway", "Raleway-Light.ttf"),
        os.path.join(font_directory, "Raleway", "Raleway-Medium.ttf"),
        os.path.join(font_directory, "Raleway", "Raleway-Regular.ttf"),
        os.path.join(font_directory, "Raleway", "Raleway-SemiBold.ttf"),
        os.path.join(font_directory, "Raleway", "Raleway-Thin.ttf"),
        os.path.join(font_directory, "Raleway", "generated_fonts", "Raleway-Black.ttf - generated.ttf"),
        os.path.join(font_directory, "Raleway", "generated_fonts", "Raleway-Bold.ttf - generated.ttf"),
        os.path.join(font_directory, "Raleway", "generated_fonts", "Raleway-BoldItalic.ttf - generated.ttf"),
        os.path.join(font_directory, "Raleway", "generated_fonts", "Raleway-ExtraBold.ttf - generated.ttf"),
        os.path.join(font_directory, "Raleway", "generated_fonts", "Raleway-ExtraLight.ttf - generated.ttf"),
        os.path.join(font_directory, "Raleway", "generated_fonts", "Raleway-Italic.ttf - generated.ttf"),
        os.path.join(font_directory, "Raleway", "generated_fonts", "Raleway-Light.ttf - generated.ttf"),
        os.path.join(font_directory, "Raleway", "generated_fonts", "Raleway-Medium.ttf - generated.ttf"),
        os.path.join(font_directory, "Raleway", "generated_fonts", "Raleway-Regular.ttf - generated.ttf"),
        os.path.join(font_directory, "Raleway", "generated_fonts", "Raleway-SemiBold.ttf - generated.ttf"),
        os.path.join(font_directory, "Raleway", "generated_fonts", "Raleway-Thin.ttf - generated.ttf"),
    ])

    assert sorted(result) == sorted(expected_result)