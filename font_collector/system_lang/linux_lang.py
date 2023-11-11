from .system_lang import SystemLang
from locale import getdefaultlocale
from typing import Optional

class LinuxLang(SystemLang):

    def get_lang() -> Optional[str]:
        lang, _ = getdefaultlocale()
        if lang is None:
            # Fallback to english if not found
            lang = "en"
        return lang
