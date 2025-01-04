from locale import getlocale

from .abc_system_lang import ABCSystemLang


class LinuxLang(ABCSystemLang):

    @staticmethod
    def get_lang() -> str:
        lang, _ = getlocale()
        # C means that the locale isn't set. See: https://docs.python.org/3/library/locale.html#locale.getlocale
        if lang is None or lang == "C":
            lang = ABCSystemLang.default_lang
        return lang
