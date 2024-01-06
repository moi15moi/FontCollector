from __future__ import annotations
from enum import auto, Enum
from langcodes import Language


class ChineseVariant(Enum):
    TRADITIONAL = auto()
    SIMPLIFIED = auto()

    @classmethod
    def from_lang_code(cls: ChineseVariant, lang_code: Language) -> ChineseVariant:
        """
        Parameters:
            TODO
        """

        if lang_code.territory in ("TW", "HK", "MO") or lang_code.script == "Hant":
            return ChineseVariant.TRADITIONAL
        return ChineseVariant.SIMPLIFIED