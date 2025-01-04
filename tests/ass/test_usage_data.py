import ast
import re

import pytest

from font_collector import UsageData


def test__init__():
    characters_used = {'A'}
    lines = {1, 2}
    usage_data = UsageData(characters_used, lines)

    assert usage_data.characters_used == characters_used
    assert usage_data.lines == lines


def test_ordered_lines_property():
    characters_used = {'A'}
    lines = {2, 1}
    usage_data = UsageData(characters_used, lines)

    assert usage_data.ordered_lines == [1, 2]

    with pytest.raises(AttributeError) as exc_info:
        usage_data.ordered_lines = "test"
    assert str(exc_info.value) == "You cannot set the ordered lines property. If you want to add an lines, set lines"


def test__eq__():
    usage_data_1 = UsageData(
        {'A', 'B'},
        {1, 2}
    )

    usage_data_2 = UsageData(
        {'A', 'B'},
        {1, 2}
    )
    assert usage_data_1 == usage_data_2


    usage_data_3 = UsageData(
        {'A'}, # Different
        {1, 2}
    )
    assert usage_data_1 != usage_data_3

    usage_data_4 = UsageData(
        {'A', 'B'},
        {1} # Different
    )

    assert usage_data_1 != usage_data_4

    assert usage_data_1 != "test"


def test__repr__():
    characters_used = {"a", "b"}
    lines = {2, 1}
    usage_data = UsageData(characters_used, lines)

    usage_data_repr = repr(usage_data)

    characters_used_str = re.findall('{.*}', usage_data_repr)[0]
    assert ast.literal_eval(characters_used_str) == characters_used

    result = re.sub('{.*}', '', usage_data_repr)
    assert result == 'UsageData(Characters used="", Lines="[1, 2]")'
