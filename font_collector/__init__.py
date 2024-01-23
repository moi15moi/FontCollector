import logging

# Packages
from .ass import *
from .font import *
from .system_lang import *
# Files
from .exceptions import *
from .mkvpropedit import *
from ._version import __version__
from fontTools.misc.loggingTools import configLogger

configLogger(level="CRITICAL")

# Set our default logger
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

_formatter = logging.Formatter("%(levelname)s - %(message)s")

_handler = logging.StreamHandler()
_handler.setLevel(logging.INFO)
_handler.setFormatter(_formatter)

_logger.addHandler(_handler)


def set_loglevel(level: int) -> None:
    """
    Args:
        level: An level from logging module (For more detail, see: https://docs.python.org/3/library/logging.html#logging-levels)
    """
    _logger.setLevel(level)
    _handler.setLevel(level)
