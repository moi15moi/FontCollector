from __future__ import annotations
from enum import auto, Enum
from fontTools.ttLib.ttFont import TTFont
from typing import Type

__all__ = ["FontType"]

class FontType(Enum):
    UNKNOWN = auto()
    TRUETYPE = auto()
    OPENTYPE = auto()
    TRUETYPE_COLLECTION = auto()
    OPENTYPE_COLLECTION = auto()

    @classmethod
    def from_font(cls: Type[FontType], font: TTFont, is_collection_font: bool) -> FontType:
        """
        Args:
            font: An fontTools object.
            is_collection_font: If true, then the file is from a collection font (.ttc of .otc)
        Returns:
            The FontType of the specified font.
        """

        if 'glyf' in font:
            return cls.TRUETYPE_COLLECTION if is_collection_font else cls.TRUETYPE
        elif 'CFF ' in font or 'CFF2' in font:
            return cls.OPENTYPE_COLLECTION if is_collection_font else cls.OPENTYPE
        else:
            return cls.UNKNOWN