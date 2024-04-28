from ..exceptions import OSNotSupported
from platform import system

__all__ = ["get_system_lang"]

def get_system_lang() -> str:
    system_name = system()

    if system_name == "Windows":
        from .windows_lang import WindowsLang
        lang = WindowsLang.get_lang()
    elif system_name == "Linux":
        from .linux_lang import LinuxLang
        lang = LinuxLang.get_lang()
    elif system_name == "Darwin":
        from .mac_lang import MacLang
        lang = MacLang.get_lang()
    else:
        raise OSNotSupported("get_lang() only works on Windows, Mac and Linux.")

    if lang is None:
        raise SystemError("Couldn't get the OS language")

    return lang
