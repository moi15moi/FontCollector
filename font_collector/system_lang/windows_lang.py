from ..font.name import Name, PlatformID
from .abc_system_lang import ABCSystemLang
from ctypes import windll, wintypes # type: ignore


class WindowsLang(ABCSystemLang):
    __kernel32 = None

    @staticmethod
    def get_lang() -> str:
        # GetSystemDefaultLangID is available since Windows 2000.
        # Python 3.8 and more doesn't support OS behind Windows XP, so we don't need to check the Windows version.

        if WindowsLang.__kernel32 is None:
            WindowsLang.__load_kernel32()
        assert WindowsLang.__kernel32 is not None # just to make mypy happy

        lang_id = WindowsLang.__kernel32.GetSystemDefaultLangID()
        return Name.get_bcp47_lang_code_from_name_record(PlatformID.MICROSOFT, lang_id)


    @staticmethod
    def __load_kernel32() -> None:
        WindowsLang.__kernel32 = windll.kernel32

        # https://learn.microsoft.com/en-us/windows/win32/api/winnls/nf-winnls-getsystemdefaultlangid
        WindowsLang.__kernel32.GetSystemDefaultLangID.restype = wintypes.LANGID
        WindowsLang.__kernel32.GetSystemDefaultLangID.argtypes = []
