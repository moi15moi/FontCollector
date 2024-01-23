from .abc_system_lang import ABCSystemLang
from locale import getlocale

class LinuxLang(ABCSystemLang):

    @staticmethod
    def get_lang() -> str:
        lang, _ = getlocale()
        if lang is None:
            lang = ABCSystemLang.default_lang
        return lang
