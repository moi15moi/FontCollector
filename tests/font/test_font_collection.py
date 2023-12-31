import os
import pytest
from font_collector import AssStyle, FontFile, FontCollection, FontLoader, FontType

dir_path = os.path.dirname(os.path.realpath(__file__))


def test__init__():
    use_system_font = False
    reload_system_font = True
    use_generated_fonts = False
    additional_fonts = set()
    font_collection = FontCollection(
        use_system_font, 
        reload_system_font, 
        use_generated_fonts, 
        additional_fonts
    )

    assert font_collection.use_system_font == use_system_font
    assert font_collection.reload_system_font == reload_system_font
    assert font_collection.additional_fonts == additional_fonts


def test_system_fonts_property():
    font_collection = FontCollection(use_system_font=False)
    assert font_collection.system_fonts == []
    font_collection.use_system_font = True
    assert len(font_collection.system_fonts) > 0

    with pytest.raises(AttributeError) as exc_info:
        font_collection.system_fonts = "test"
    assert str(exc_info.value) == "You cannot set system_fonts, but you can set use_system_font"


def test_generated_fonts_property():
    # It could be any font
    font_file = FontFile.from_font_path(os.path.join(os.path.dirname(dir_path), "file", "variable font tests", "Test #6", "Test #6.ttf"))

    font_collection = FontCollection(use_generated_fonts=False)
    assert len(font_collection.generated_fonts) == 0

    font_collection.use_generated_fonts = True
    nbr_generated_font_before = len(font_collection.generated_fonts)
    FontLoader.add_generated_font(font_file)
    nbr_generated_font_after = len(font_collection.generated_fonts)
    assert nbr_generated_font_before + 1 == nbr_generated_font_after

    with pytest.raises(AttributeError) as exc_info:
        font_collection.generated_fonts = "test"
    assert str(exc_info.value) == "You cannot set generated_fonts, but you can set use_generated_fonts"


def test_fonts_property():
    font_collection = FontCollection(use_system_font=False)

    with pytest.raises(AttributeError) as exc_info:
        font_collection.fonts = "test"
    assert str(exc_info.value) == "You cannot set the fonts. If you want to add font, set additional_fonts"


def test_get_used_font_by_style():
    fonts_path = os.path.join(os.path.dirname(dir_path), "file", "fonts", "Raleway", "generated_fonts")
    additional_fonts = FontLoader.load_additional_fonts([fonts_path])            

    font_collection = FontCollection(use_system_font=False, additional_fonts=additional_fonts)

    ass_style = AssStyle("Raleway", 900, True)
    font_result = font_collection.get_used_font_by_style(ass_style)

    # VSFilter prefer to match to the weight then the italic.
    # If it would have prefer to match the italic, the weight would be 700 and italic would be true.
    assert font_result.font_face.weight == 900
    assert font_result.font_face.is_italic == False

    ass_style = AssStyle("Font name that isn't in the FontCollection", 900, True)
    font_result = font_collection.get_used_font_by_style(ass_style)
    assert font_result == None


def test_get_used_font_by_style_otf_vs_ttf():
    alivia_generated_font_path = os.path.join(os.path.dirname(dir_path), "file", "fonts", "Same Font, but otf vs ttf", "Alivia - Generated.ttf")
    alivia_otf_font_path = os.path.join(os.path.dirname(dir_path), "file", "fonts", "Same Font, but otf vs ttf", "Alivia.otf")

    with open(alivia_generated_font_path, 'rb') as file:
        alivia_generated_content = file.read()

    with open(alivia_otf_font_path, 'rb') as file:
        alivia_otf_content = file.read()

    os.remove(alivia_generated_font_path)
    os.remove(alivia_otf_font_path)

    # Important, we create the otf file before the ttf file
    with open(alivia_otf_font_path, 'wb') as file:
        file.write(alivia_otf_content)

    with open(alivia_generated_font_path, 'wb') as file:
        file.write(alivia_generated_content)

    additional_fonts = FontLoader.load_additional_fonts([alivia_generated_font_path, alivia_otf_font_path])
    font_collection = FontCollection(use_system_font=False, additional_fonts=additional_fonts)

    ass_style = AssStyle("Alivia", 400, False)
    font_result = font_collection.get_used_font_by_style(ass_style)

    assert font_result.font_face.font_file.filename == alivia_generated_font_path


def test__eq__():
    pass


def test__hash__():
    pass

def test__repr__():
    font_collection = FontCollection(
        use_system_font=False,
        reload_system_font=False,
        use_generated_fonts=False,
        additional_fonts=set()
    )

    assert repr(font_collection) == 'FontCollection(Use system font="False", Reload system font="False", Use generated fonts="False", Additional fonts="set()")'