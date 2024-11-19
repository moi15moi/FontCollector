import os
from platform import system
import pytest
import shutil
from font_collector import (
    AssStyle,
    FontFile,
    FontCollection,
    FontLoader,
    FontType,
    FontResult,
    FontSelectionStrategyLibass,
    Name,
    NormalFontFace,
    VariableFontFace
)
from langcodes import Language
from pathlib import Path
from time import sleep
from typing import Hashable

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


def test_iterator():
    font_mac_platform = Path(os.path.join(os.path.dirname(dir_path), "file", "fonts", "font_mac.TTF"))
    font_faces_1 = [NormalFontFace(0, [Name("family_1", Language.get("en"))], [Name("exact_1", Language.get("en"))], 400, False, False, FontType.TRUETYPE)]
    font_file_1 = FontFile(font_mac_platform, font_faces_1, False)
    font_faces_2 = [NormalFontFace(0, [Name("family_2", Language.get("en"))], [Name("exact_2", Language.get("en"))], 400, False, False, FontType.TRUETYPE)]
    font_file_2 = FontFile(font_mac_platform, font_faces_2, False)
    additional_fonts =[font_file_1, font_file_2]

    font_collection = FontCollection(False, use_generated_fonts=False, additional_fonts=[])
    for idx, font in enumerate(font_collection):
        assert font == additional_fonts[idx]


def test_empty_iterator():
    font_collection = FontCollection(False, use_generated_fonts=False, additional_fonts=[])
    assert list(font_collection) == []


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
    font_file = FontFile.from_font_path(Path(os.path.join(os.path.dirname(dir_path), "file", "variable font tests", "Test #6", "Test #6.ttf")))

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
    fonts_path = Path(os.path.join(os.path.dirname(dir_path), "file", "fonts", "Raleway", "generated_fonts"))
    additional_fonts = FontLoader.load_additional_fonts([fonts_path])

    font_collection = FontCollection(use_system_font=False, use_generated_fonts=False, additional_fonts=additional_fonts)
    strategy = FontSelectionStrategyLibass()

    ass_style = AssStyle("Raleway", 900, True)
    font_result = font_collection.get_used_font_by_style(ass_style, strategy)

    # VSFilter prefer to match to the weight then the italic.
    # If it would have prefer to match the italic, the weight would be 700 and italic would be true.
    assert font_result.font_face.weight == 900
    assert font_result.font_face.is_italic == False

    ass_style = AssStyle("Font name that isn't in the FontCollection", 900, True)
    font_result = font_collection.get_used_font_by_style(ass_style, strategy)
    assert font_result == None

    # Test if it match exact_names
    font_mac_platform = Path(os.path.join(os.path.dirname(dir_path), "file", "fonts", "font_mac.TTF"))
    font_faces = [NormalFontFace(0, [Name("family", Language.get("en"))], [Name("exact", Language.get("en"))], 400, False, False, FontType.TRUETYPE)]
    font_file = FontFile(font_mac_platform, font_faces, False)
    font_collection = FontCollection(use_system_font=False, use_generated_fonts=False, additional_fonts=[font_file])
    ass_style = AssStyle("exact", 900, True)
    font_result = font_collection.get_used_font_by_style(ass_style, strategy)
    assert font_result == FontResult(font_faces[0], True, True, True)

    # FontFile with same attributes (except last_loaded_time). In this case, the algorithm will use the older font
    sf_pro_display = Path(os.path.join(os.path.dirname(dir_path), "file", "fonts", "SFProDisplay-Bold.ttf"))
    sf_pro_display_italic = Path(os.path.join(os.path.dirname(dir_path), "file", "fonts", "SFProDisplay-BoldItalic.ttf"))
    sf_pro_display_temp = Path(os.path.join(os.path.dirname(dir_path), "file", "fonts", "SFProDisplay-Bold - Temp.ttf"))
    sf_pro_display_italic_temp = Path(os.path.join(os.path.dirname(dir_path), "file", "fonts", "SFProDisplay-BoldItalic - Temp.ttf"))

    shutil.copy2(sf_pro_display, sf_pro_display_temp)
    sleep(1)
    shutil.copy2(sf_pro_display_italic, sf_pro_display_italic_temp)

    sf_pro_display_temp_font = FontFile.from_font_path(sf_pro_display_temp)
    sf_pro_display_italic_temp_font = FontFile.from_font_path(sf_pro_display_italic_temp)
    additional_fonts = [sf_pro_display_temp_font, sf_pro_display_italic_temp_font]
    font_collection = FontCollection(use_system_font=False, use_generated_fonts=False, additional_fonts=additional_fonts)
    ass_style = AssStyle("SF Pro Display", 400, False)
    result = font_collection.get_used_font_by_style(ass_style, strategy)
    assert result.font_face == sf_pro_display_temp_font.font_faces[0]

    os.remove(sf_pro_display_italic_temp)
    os.remove(sf_pro_display_temp)

    # Same test has the previous one, but here SFProDisplay-BoldItalic is older than SFProDisplay-Bold
    sf_pro_display_temp_2 = Path(os.path.join(os.path.dirname(dir_path), "file", "fonts", "SFProDisplay-Bold - Temp 2.ttf"))
    sf_pro_display_italic_temp_2 = Path(os.path.join(os.path.dirname(dir_path), "file", "fonts", "SFProDisplay-BoldItalic - Temp 2.ttf"))

    shutil.copy2(sf_pro_display_italic, sf_pro_display_italic_temp_2)
    sleep(1)
    shutil.copy2(sf_pro_display, sf_pro_display_temp_2)

    sf_pro_display_temp_font_2 = FontFile.from_font_path(sf_pro_display_temp_2)
    sf_pro_display_italic_temp_font_2 = FontFile.from_font_path(sf_pro_display_italic_temp_2)
    additional_fonts = [sf_pro_display_temp_font_2, sf_pro_display_italic_temp_font_2]
    font_collection = FontCollection(use_system_font=False, use_generated_fonts=False, additional_fonts=additional_fonts)
    result = font_collection.get_used_font_by_style(ass_style, strategy)
    assert result.font_face == sf_pro_display_italic_temp_font.font_faces[0]

    os.remove(sf_pro_display_temp_2)
    os.remove(sf_pro_display_italic_temp_2)


def test__eq__():
    font_collection_1 = FontCollection(True, True, True, [])
    font_collection_2 = FontCollection(True, True, True, [])

    assert font_collection_1 == font_collection_2

    font_collection_3 = FontCollection(False, True, True, [])
    assert font_collection_1 != font_collection_3

    font_collection_4 = FontCollection(True, False, True, [])
    assert font_collection_1 != font_collection_4

    font_collection_5 = FontCollection(True, True, False, [])
    assert font_collection_1 != font_collection_5

    font_mac_platform = Path(os.path.join(os.path.dirname(dir_path), "file", "fonts", "font_mac.TTF"))
    font_faces = [
        VariableFontFace(0, [Name("test", Language.get("en"))], [], [], 400, False, FontType.TRUETYPE, {}),
    ]
    font_file = FontFile(font_mac_platform, font_faces, False)
    font_collection_6 = FontCollection(True, True, True, [font_file])
    assert font_collection_1 != font_collection_6

    assert font_collection_1 != "test"


def test__hash__():
    font_collection_1 = FontCollection(True, True, True, [])
    font_collection_2 = FontCollection(True, True, True, [])
    assert isinstance(font_collection_1, Hashable)
    assert {font_collection_1} == {font_collection_2}

    font_collection_3 = FontCollection(False, True, True, [])
    assert {font_collection_1} != {font_collection_3}

    font_collection_4 = FontCollection(True, False, True, [])
    assert {font_collection_1} != {font_collection_4}

    font_collection_5 = FontCollection(True, True, False, [])
    assert {font_collection_1} != {font_collection_5}

    font_mac_platform = Path(os.path.join(os.path.dirname(dir_path), "file", "fonts", "font_mac.TTF"))
    font_faces = [
        VariableFontFace(0, [Name("test", Language.get("en"))], [], [], 400, False, FontType.TRUETYPE, {}),
    ]
    font_file = FontFile(font_mac_platform, font_faces, False)
    font_collection_6 = FontCollection(True, True, True, [font_file])
    assert {font_collection_1} != {font_collection_6}

    assert {font_collection_1} != {"test"}


def test__repr__():
    font_collection = FontCollection(
        use_system_font=False,
        reload_system_font=False,
        use_generated_fonts=False,
        additional_fonts=set()
    )

    assert repr(font_collection) == 'FontCollection(Use system font="False", Reload system font="False", Use generated fonts="False", Additional fonts="set()")'


@pytest.mark.skipif(system() != "Darwin", reason="Test runs only on Darwin")
def test_BM_Kirang_Haerang():
    # This is just a temporary test to try what XMX says here: https://discord.com/channels/131816223523602432/710562732973490238/1308566022122377328s
    font_collection = FontCollection(use_system_font=True)
    strategy = FontSelectionStrategyLibass()

    ass_style = AssStyle("BMKIRANGHAERANG-OTF", 400, False)
    font_result = font_collection.get_used_font_by_style(ass_style, strategy)
    assert font_result != None
    assert font_result.font_face.font_file.filename.is_file()
