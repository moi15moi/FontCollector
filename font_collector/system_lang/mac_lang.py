from ctypes import (
    c_bool,
    c_char_p,
    c_long,
    c_uint32,
    c_void_p,
    cdll,
    create_string_buffer,
    util
)

from find_system_fonts_filename.mac.version_helpers import MacVersionHelpers

from ..exceptions import OSNotSupported
from .abc_system_lang import ABCSystemLang


class MacLang(ABCSystemLang):
    __core_foundation = None
    kCFStringEncodingUTF8 = 0x08000100 # https://developer.apple.com/documentation/corefoundation/cfstringbuiltinencodings/kcfstringencodingutf8?language=objc

    @staticmethod
    def get_lang() -> str:
        if not MacVersionHelpers.is_mac_version_or_greater(10, 5):
            raise OSNotSupported("get_lang() only works on mac 10.5 or more")

        if MacLang.__core_foundation is None:
            MacLang.__load__core_foundation()
        assert MacLang.__core_foundation is not None # just to make mypy happy

        languages = MacLang.__core_foundation.CFLocaleCopyPreferredLanguages()
        languages_count = MacLang.__core_foundation.CFArrayGetCount(languages)

        if languages_count == 0:
            # Fallback to english if not found
            return ABCSystemLang.default_lang

        language = MacLang.__core_foundation.CFArrayGetValueAtIndex(languages, 0)
        language_str = MacLang.__cfstring_to_string(language)

        MacLang.__core_foundation.CFRelease(languages)
        return language_str


    @staticmethod
    def __cfstring_to_string(cfstring: c_void_p) -> str:
        """
        Args:
            cfstring: An CFString instance.
        Returns:
            The decoded CFString.
        """
        assert MacLang.__core_foundation is not None # just to make mypy happy

        length = MacLang.__core_foundation.CFStringGetLength(cfstring)
        size = MacLang.__core_foundation.CFStringGetMaximumSizeForEncoding(length, MacLang.kCFStringEncodingUTF8)
        buffer = create_string_buffer(size + 1)
        result = MacLang.__core_foundation.CFStringGetCString(cfstring, buffer, len(buffer), MacLang.kCFStringEncodingUTF8)
        if result:
            return str(buffer.value, 'utf-8')
        else:
            raise Exception("An unexpected error has occurred while decoding the CFString.")


    @staticmethod
    def __load__core_foundation() -> None:
        core_foundation_library_name = util.find_library("CoreFoundation")
        # Hack for compatibility with macOS greater or equals to 11.0.
        # From: https://github.com/pyglet/pyglet/blob/a44e83a265e7df8ece793de865bcf3690f66adbd/pyglet/libs/darwin/cocoapy/cocoalibs.py#L10-L14
        if core_foundation_library_name is None:
            core_foundation_library_name = "/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation"
        MacLang.__core_foundation = cdll.LoadLibrary(core_foundation_library_name)

        CFIndex = c_long
        CFStringEncoding = c_uint32

        # https://developer.apple.com/documentation/corefoundation/1521153-cfrelease
        MacLang.__core_foundation.CFRelease.restype = c_void_p
        MacLang.__core_foundation.CFRelease.argtypes = [c_void_p]

        # https://developer.apple.com/documentation/corefoundation/1388772-cfarraygetcount?language=objc
        MacLang.__core_foundation.CFArrayGetCount.restype = CFIndex
        MacLang.__core_foundation.CFArrayGetCount.argtypes = [c_void_p]

        # https://developer.apple.com/documentation/corefoundation/1388767-cfarraygetvalueatindex?language=objc
        MacLang.__core_foundation.CFArrayGetValueAtIndex.restype = c_void_p
        MacLang.__core_foundation.CFArrayGetValueAtIndex.argtypes = [c_void_p, CFIndex]

        # https://developer.apple.com/documentation/corefoundation/1542853-cfstringgetlength?language=objc
        MacLang.__core_foundation.CFStringGetLength.restype = CFIndex
        MacLang.__core_foundation.CFStringGetLength.argtypes = [c_void_p]

        # https://developer.apple.com/documentation/corefoundation/1542143-cfstringgetmaximumsizeforencodin?language=objc
        MacLang.__core_foundation.CFStringGetMaximumSizeForEncoding.restype = CFIndex
        MacLang.__core_foundation.CFStringGetMaximumSizeForEncoding.argtypes = [c_void_p, CFStringEncoding]

        # https://developer.apple.com/documentation/corefoundation/1542721-cfstringgetcstring?language=objc
        MacLang.__core_foundation.CFStringGetCString.restype = c_bool
        MacLang.__core_foundation.CFStringGetCString.argtypes = [c_void_p, c_char_p, CFIndex, CFStringEncoding]

        # https://developer.apple.com/documentation/corefoundation/1542887-cflocalecopypreferredlanguages?language=objc
        MacLang.__core_foundation.CFLocaleCopyPreferredLanguages.restype = c_void_p
        MacLang.__core_foundation.CFLocaleCopyPreferredLanguages.argtypes = []
