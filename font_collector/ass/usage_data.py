from __future__ import annotations
from typing import Any, Set


class UsageData:

    characters_used: Set[str]
    lines: Set[int]

    def __init__(
        self: UsageData,
        characters_used: Set[str],
        lines: Set[int],
    ):
        self.characters_used = characters_used
        self.lines = lines

    @property
    def ordered_lines(self: UsageData):
        lines = list(self.lines)
        lines.sort()
        return lines

    @ordered_lines.setter
    def ordered_lines(self: UsageData, value: Any):
        raise AttributeError("You cannot set the ordered lines property. If you want to add an lines, set lines")

    def __eq__(self: UsageData, other: UsageData):
        return (self.characters_used, self.lines) == (
            other.characters_used,
            other.lines,
        )

    def __repr__(self: UsageData):
        return f'UsageData(Characters used="{self.characters_used}", Lines="{self.ordered_lines}")'
