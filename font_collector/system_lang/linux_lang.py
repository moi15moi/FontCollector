from .abc_system_lang import ABCSystemLang
from locale import getdefaultlocale

class LinuxLang(ABCSystemLang):

    @staticmethod
    def get_lang() -> str:
        lang, _ = getdefaultlocale()
        if lang is None:
            lang = ABCSystemLang.default_lang
        return lang
