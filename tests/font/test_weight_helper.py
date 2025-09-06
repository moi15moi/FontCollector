import pytest
from font_collector import font_weight_to_name


@pytest.mark.parametrize("weight,expected", [
    (50, "Thin"),
    (100, "Thin"),
    (150, "Thin"),
    (151, "ExtraLight"),
    (200, "ExtraLight"),
    (250, "ExtraLight"),
    (251, "Light"),
    (300, "Light"),
    (350, "Light"),
    (351, "Regular"),
    (400, "Regular"),
    (450, "Regular"),
    (451, "Medium"),
    (500, "Medium"),
    (550, "Medium"),
    (551, "SemiBold"),
    (600, "SemiBold"),
    (650, "SemiBold"),
    (651, "Bold"),
    (700, "Bold"),
    (750, "Bold"),
    (751, "ExtraBold"),
    (800, "ExtraBold"),
    (850, "ExtraBold"),
    (851, "Black"),
    (900, "Black"),
    (1000, "Black"),
])
def test_font_weight_to_name(weight, expected):
    assert font_weight_to_name(weight) == expected
