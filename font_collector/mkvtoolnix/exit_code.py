from enum import IntEnum

__all__ = ["ExitCode"]


class ExitCode(IntEnum):
    # From https://mkvtoolnix.download/doc/mkvpropedit.html#d4e1266
    # All the MKVToolNix programs use this enumeration
    SUCCESS = 0
    WARNING = 1
    ERROR = 2
