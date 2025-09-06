from __future__ import annotations

__all__ = ["font_weight_to_name"]

def font_weight_to_name(weight: int) -> str:
    """
    Args:
        weight: The weight of a font as defined in usWeightClass:. https://learn.microsoft.com/en-us/typography/opentype/spec/os2#usweightclass
    Returns:
        The name corresponding to the weight.
    """
    if weight <= 150:
        return "Thin"
    elif 151 <= weight <= 250:
        return "ExtraLight"
    elif 251 <= weight <= 350:
        return "Light"
    elif 351 <= weight <= 450:
        return "Regular"
    elif 451 <= weight <= 550:
        return "Medium"
    elif 551 <= weight <= 650:
        return "SemiBold"
    elif 651 <= weight <= 750:
        return "Bold"
    elif 751 <= weight <= 850:
        return "ExtraBold"
    else:
        return "Black"
