from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, List, Set

__all__ = ["UsageData"]

class UsageData:

    characters_used: Set[str]
    lines: Set[int]

    def __init__(
        self: UsageData,
        characters_used: Set[str],
        lines: Set[int],
    ) -> None:
        self.characters_used = characters_used
        self.lines = lines


    @property
    def ordered_lines(self: UsageData) -> List[int]:
        lines = list(self.lines)
        lines.sort()
        return lines


    @ordered_lines.setter
    def ordered_lines(self: UsageData, value: Any) -> None:
        raise AttributeError("You cannot set the ordered lines property. If you want to add an lines, set lines")


    def __eq__(self: UsageData, other: object) -> bool:
        if not isinstance(other, UsageData):
            return False
        return (self.characters_used, self.lines) == (
            other.characters_used,
            other.lines,
        )


    def __repr__(self: UsageData) -> str:
        return f'{self.__class__.__name__}(Characters used="{self.characters_used}", Lines="{self.ordered_lines}")'
