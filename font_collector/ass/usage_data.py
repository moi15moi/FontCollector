from __future__ import annotations
from typing import Any

__all__ = ["UsageData"]

class UsageData:
    """Represent the characters used in a set of lines of a .ass file

    Attributes:
        characters_used: A set of characters used in the set of lines.
        lines: A set containing the indices of lines in a .ass file.
    """


    def __init__(
        self,
        characters_used: set[str],
        lines: set[int],
    ) -> None:
        self.characters_used = characters_used
        self.lines = lines


    @property
    def ordered_lines(self) -> list[int]:
        """
        Returns:
            A sorted list containing the indices of lines in a .ass file.
            Each value represent a index of a .ass file line.

        """
        lines = list(self.lines)
        lines.sort()
        return lines


    @ordered_lines.setter
    def ordered_lines(self, value: Any) -> None:
        raise AttributeError("You cannot set the ordered lines property. If you want to add an lines, set lines")


    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UsageData):
            return False
        return (self.characters_used, self.lines) == (
            other.characters_used,
            other.lines,
        )


    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(Characters used="{self.characters_used}", Lines="{self.ordered_lines}")'
