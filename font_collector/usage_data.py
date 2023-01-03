from typing import Set


class UsageData:

    characters_used: Set[str]
    lines: Set[int]

    def __init__(
        self,
        characters_used: Set[str],
        lines: Set[int],
    ):
        self.characters_used = characters_used
        self.lines = lines

    @property
    def ordered_lines(self):
        lines = list(self.lines)
        lines.sort()
        return lines

    def __eq__(self, other: "UsageData"):
        return (self.characters_used, self.lines) == (
            other.characters_used,
            other.lines,
        )

    def __repr__(self):
        return f'characters_used: "{self.characters_used}", lines: "{self.lines}"'
