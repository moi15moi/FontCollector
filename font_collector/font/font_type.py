from __future__ import annotations
from enum import auto, Enum
from fontTools.ttLib.ttFont import TTFont


class FontType(Enum):
    UNKNOWN = auto()
    TRUETYPE = auto()
    OPENTYPE = auto()
    TRUETYPE_COLLECTION = auto()
    OPENTYPE_COLLECTION = auto()

    @classmethod
    def from_font(cls: FontType, font: TTFont, is_collection_font: bool) -> FontType:
        """
        Parameters:
            font (TTFont): An fontTools object.
            is_collection_font (bool): If true, then the file is from a collection font.
        """

        if 'glyf' in font:
            return cls.TRUETYPE_COLLECTION if is_collection_font else cls.TRUETYPE
        elif 'CFF ' in font or 'CFF2' in font:
            return cls.OPENTYPE_COLLECTION if is_collection_font else cls.OPENTYPE
        else:
            return cls.UNKNOWN