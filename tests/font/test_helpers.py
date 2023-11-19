import os

from langcodes import Language
from font_collector import FactoryABCFont, Helpers, Font, Name, FontType

dir_path = os.path.dirname(os.path.realpath(__file__))


def test_variable_font_to_collection():
    font_path = os.path.join(os.path.dirname(dir_path), "fonts", "Asap-VariableFont_wdth,wght.ttf")
    font_index = 0
    save_path = os.path.join(dir_path, "Asap - Test.ttf")
    try:
        Helpers.variable_font_to_collection(font_path, font_index, save_path)
        generated_fonts = FactoryABCFont.from_font_path(save_path)
    except Exception:
        pass
    finally:
        # Always delete the generated font
        if os.path.isfile(save_path):
            os.remove(save_path)

    expected_fonts = [
        Font(
            save_path,
            0,
            [Name("Asap Thin", Language.get("en"))],
            [Name("Asap Thin", Language.get("en"))],
            100,
            False,
            False,
            FontType.TRUETYPE_COLLECTION
        ),
        Font(
            save_path,
            1,
            [Name("Asap ExtraLight", Language.get("en"))],
            [Name("Asap ExtraLight", Language.get("en"))],
            200,
            False,
            False,
            FontType.TRUETYPE_COLLECTION
        ),
        Font(
            save_path,
            2,
            [Name("Asap Light", Language.get("en"))],
            [Name("Asap Light", Language.get("en"))],
            300,
            False,
            False,
            FontType.TRUETYPE_COLLECTION
        ),
        Font(
            save_path,
            3,
            [Name("Asap", Language.get("en"))],
            [Name("Asap Regular", Language.get("en"))],
            400,
            False,
            False,
            FontType.TRUETYPE_COLLECTION
        ),
        Font(
            save_path,
            4,
            [Name("Asap Medium", Language.get("en"))],
            [Name("Asap Medium", Language.get("en"))],
            500,
            False,
            True,
            FontType.TRUETYPE_COLLECTION
        ),
        Font(
            save_path,
            5,
            [Name("Asap SemiBold", Language.get("en"))],
            [Name("Asap SemiBold", Language.get("en"))],
            600,
            False,
            True,
            FontType.TRUETYPE_COLLECTION
        ),
        Font(
            save_path,
            6,
            [Name("Asap", Language.get("en"))],
            [Name("Asap Bold", Language.get("en"))],
            700,
            False,
            True,
            FontType.TRUETYPE_COLLECTION
        ),
        Font(
            save_path,
            7,
            [Name("Asap ExtraBold", Language.get("en"))],
            [Name("Asap ExtraBold", Language.get("en"))],
            800,
            False,
            True,
            FontType.TRUETYPE_COLLECTION
        ),
        Font(
            save_path,
            8,
            [Name("Asap Black", Language.get("en"))],
            [Name("Asap Black", Language.get("en"))],
            900,
            False,
            True,
            FontType.TRUETYPE_COLLECTION
        )
    ]

    # The generated collection can be in any order. To test it, we need to try all the possible font_index
    for font in expected_fonts:
        font_found = False

        for i in range(len(expected_fonts)):
            font.font_index = i
            if font in generated_fonts:
                font_found = True
                break
        
        assert font_found