__all__ = [
    "InvalidNameRecord",
    "InvalidFontException",
    "InvalidNormalFontFaceException",
    "InvalidVariableFontFaceException",
    "InvalidLanguageCode",
    "OSNotSupported",
]

class InvalidNameRecord(Exception):
    "Raised when a NameRecord isn't supported by GDI"


class InvalidFontException(Exception):
    "Raised when a font (can be a normal font or a variable font) isn't valid"


class InvalidNormalFontFaceException(InvalidFontException):
    "Raised when a normal font isn't valid"


class InvalidVariableFontFaceException(InvalidFontException):
    "Raised when a variable font isn't valid"


class InvalidLanguageCode(ValueError):
    "Raised when a string does not conform to IETF BCP-47."


class OSNotSupported(Exception):
    "Raised when an OS isn't supported"
