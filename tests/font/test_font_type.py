import os

from fontTools.ttLib.ttFont import TTFont

from font_collector import FontType

dir_path = os.path.dirname(os.path.realpath(__file__))


def test_from_font():
    font_path = os.path.join(os.path.dirname(dir_path), "file", "fonts", "PENBOX.otf")
    opentype_font = TTFont(font_path)
    assert FontType.from_font(opentype_font) == FontType.OPENTYPE

    font_path = os.path.join(os.path.dirname(dir_path), "file", "fonts", "font_mac.TTF")
    truetype_font = TTFont(font_path)
    assert FontType.from_font(truetype_font) == FontType.TRUETYPE

    font_path = os.path.join(os.path.dirname(dir_path), "file", "fonts", "opentype_font_collection.ttc")
    opentype_collection_font = TTFont(font_path, fontNumber=0)
    assert FontType.from_font(opentype_collection_font) == FontType.OPENTYPE

    font_path = os.path.join(os.path.dirname(dir_path), "file", "fonts", "truetype_font_collection.ttc")
    truetype_collection_font = TTFont(font_path, fontNumber=0)
    assert FontType.from_font(truetype_collection_font) == FontType.TRUETYPE
