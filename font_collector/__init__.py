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


class IndentMultilineFormatter(logging.Formatter):
    def __init__(self) -> None:
        super().__init__("%(levelname)s - %(message)s")

    def format(self, record: logging.LogRecord) -> str:
        s = super().format(record)
        head, *tail = s.splitlines()
        indent = " " * (len(record.levelname) + 3)  # "LEVEL - " length
        s = "\n".join([head] + [indent + line for line in tail])
        return s


configLogger(level="CRITICAL")

# Set our default logger
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

_formatter = IndentMultilineFormatter()

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
