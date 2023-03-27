import logging
from .ass_document import AssDocument
from .ass_style import AssStyle
from .exceptions import InvalidFontException, NameNotFoundException
from .font_loader import FontLoader
from .font_result import FontResult
from .font import Font
from .helpers import Helpers
from .mkvpropedit import Mkvpropedit
from .usage_data import UsageData
from ._version import __version__

# Set dependency log level to ERROR
from matplotlib import set_loglevel

set_loglevel("ERROR")

from fontTools.misc.loggingTools import configLogger

configLogger(level="ERROR")

# Set our default logger
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

_formatter = logging.Formatter("%(levelname)s - %(message)s")

_handler = logging.StreamHandler()
_handler.setLevel(logging.INFO)
_handler.setFormatter(_formatter)

_logger.addHandler(_handler)


def set_loglevel(level: int):
    """
    Parameters:
        level (int): An level from logging module (For more detail, see: https://docs.python.org/3/library/logging.html#logging-levels)
    """
    _logger.setLevel(level)
    _handler.setLevel(level)
