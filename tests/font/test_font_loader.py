import os
from pathlib import Path

from font_collector import FontLoader

dir_path = os.path.dirname(os.path.realpath(__file__))


def test_load_additional_fonts():
    # Test 1
    font_file = os.path.join(os.path.dirname(dir_path), "file", "fonts", "Asap-VariableFont_wdth,wght.ttf")
    fonts_result = FontLoader.load_additional_fonts([Path(font_file)])
    result = list({font.filename for font in fonts_result})
    expected_result = [
        Path(font_file),
    ]
    assert sorted(result) == sorted(expected_result)


    # Test 2
    font_directory = os.path.join(os.path.dirname(dir_path), "file", "fonts")
    fonts_result = FontLoader.load_additional_fonts([Path(font_directory)])
    result = list({font.filename for font in fonts_result})
    expected_result = [
        Path(os.path.join(font_directory, "Asap-VariableFont_wdth,wght.ttf")),
        Path(os.path.join(font_directory, "Cabin VF Beta Regular.ttf")),
        Path(os.path.join(font_directory, "font_cmap_encoding_0.ttf")),
        Path(os.path.join(font_directory, "font_cmap_encoding_1.ttf")),
        Path(os.path.join(font_directory, "font_cmap_encoding_2.TTF")),
        Path(os.path.join(font_directory, "font_mac.TTF")),
        Path(os.path.join(font_directory, "font_with_invalid_os2_table.ttf")),
        Path(os.path.join(font_directory, "font_without axis_value.ttf")),
        Path(os.path.join(font_directory, "fvar_with_0_instance.ttf")),
        Path(os.path.join(font_directory, "invalid_cmap.ttf")),
        Path(os.path.join(font_directory, "opentype_font_collection.ttc")),
        Path(os.path.join(font_directory, "PENBOX.otf")),
        Path(os.path.join(font_directory, "SFProDisplay-Bold.ttf")),
        Path(os.path.join(font_directory, "SFProDisplay-BoldItalic.ttf")),
        Path(os.path.join(font_directory, "truetype_font_collection.ttc")),
    ]
    assert sorted(result) == sorted(expected_result)

    # Test 3
    font_directory_sub_dir = os.path.join(os.path.dirname(dir_path), "file", "fonts", "Raleway")
    fonts_result = FontLoader.load_additional_fonts([Path(font_directory_sub_dir)], scan_subdirs=True)
    result = list({font.filename for font in fonts_result})
    expected_result = [
        Path(os.path.join(font_directory_sub_dir, "Raleway-Black.ttf")),
        Path(os.path.join(font_directory_sub_dir, "Raleway-Bold.ttf")),
        Path(os.path.join(font_directory_sub_dir, "Raleway-BoldItalic.ttf")),
        Path(os.path.join(font_directory_sub_dir, "Raleway-ExtraBold.ttf")),
        Path(os.path.join(font_directory_sub_dir, "Raleway-ExtraLight.ttf")),
        Path(os.path.join(font_directory_sub_dir, "Raleway-Italic.ttf")),
        Path(os.path.join(font_directory_sub_dir, "Raleway-Light.ttf")),
        Path(os.path.join(font_directory_sub_dir, "Raleway-Medium.ttf")),
        Path(os.path.join(font_directory_sub_dir, "Raleway-Regular.ttf")),
        Path(os.path.join(font_directory_sub_dir, "Raleway-SemiBold.ttf")),
        Path(os.path.join(font_directory_sub_dir, "Raleway-Thin.ttf")),
        Path(os.path.join(font_directory_sub_dir, "generated_fonts", "Raleway-Black.ttf - generated.ttf")),
        Path(os.path.join(font_directory_sub_dir, "generated_fonts", "Raleway-Bold.ttf - generated.ttf")),
        Path(os.path.join(font_directory_sub_dir, "generated_fonts", "Raleway-BoldItalic.ttf - generated.ttf")),
        Path(os.path.join(font_directory_sub_dir, "generated_fonts", "Raleway-ExtraBold.ttf - generated.ttf")),
        Path(os.path.join(font_directory_sub_dir, "generated_fonts", "Raleway-ExtraLight.ttf - generated.ttf")),
        Path(os.path.join(font_directory_sub_dir, "generated_fonts", "Raleway-Italic.ttf - generated.ttf")),
        Path(os.path.join(font_directory_sub_dir, "generated_fonts", "Raleway-Light.ttf - generated.ttf")),
        Path(os.path.join(font_directory_sub_dir, "generated_fonts", "Raleway-Medium.ttf - generated.ttf")),
        Path(os.path.join(font_directory_sub_dir, "generated_fonts", "Raleway-Regular.ttf - generated.ttf")),
        Path(os.path.join(font_directory_sub_dir, "generated_fonts", "Raleway-SemiBold.ttf - generated.ttf")),
        Path(os.path.join(font_directory_sub_dir, "generated_fonts", "Raleway-Thin.ttf - generated.ttf")),
    ]
    assert sorted(result) == sorted(expected_result)
