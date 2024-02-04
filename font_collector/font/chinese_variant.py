from __future__ import annotations
from enum import auto, Enum
from langcodes import Language
from typing import Type


class ChineseVariant(Enum):
    TRADITIONAL = auto()
    SIMPLIFIED = auto()

    @classmethod
    def from_lang_code(cls: Type[ChineseVariant], lang_code: Language) -> ChineseVariant:
        if lang_code.language != "zh":
            raise ValueError(f"The language {lang_code} isn't chinese.")

        if lang_code.territory in ("TW", "HK", "MO") or lang_code.script == "Hant":
            return ChineseVariant.TRADITIONAL
        return ChineseVariant.SIMPLIFIED
