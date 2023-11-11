from ..font.name import Name, PlatformID
from .system_lang import SystemLang
from ctypes import windll, wintypes


class WindowsLang(SystemLang):
    __kernel32 = None

    def get_lang() -> str:
        # GetUserDefaultLangID is available since Windows 2000.
        # Python 3.8 and more doesn't support OS behind Windows XP, so we don't need to check the Windows version.

        if WindowsLang.__kernel32 is None:
            WindowsLang.__load_kernel32()

        lang_id = WindowsLang.__kernel32.GetUserDefaultLangID()
        return Name.get_lang_code_from_platform_lang_id(PlatformID.MICROSOFT, lang_id)


    @staticmethod
    def __load_kernel32():
        WindowsLang.__kernel32 = windll.kernel32

        # https://learn.microsoft.com/en-us/windows/win32/api/winnls/nf-winnls-getuserdefaultlangid
        WindowsLang.__kernel32.GetUserDefaultLangID.restype = wintypes.LANGID
        WindowsLang.__kernel32.GetUserDefaultLangID.argtypes = []