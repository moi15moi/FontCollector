from __future__ import annotations
from .._version import __version__
from .abc_font import ABCFont, FontType
from .name import Name
from itertools import product
from os import PathLike
from typing import Any, Dict, List, Set


class VariableFont(ABCFont):

    def __init__(
        self: VariableFont,
        filename: PathLike[str],
        font_index: int,
        families_prefix: List[Name],
        families_suffix: List[Name],
        exact_names_suffix: List[Name],
        weight: int,
        is_italic: bool,
        font_type: FontType,
        named_instance_coordinates: Dict[str, float],
    ):
        self.filename = filename
        self.font_index = font_index
        self.families_prefix = families_prefix
        self.families_suffix = families_suffix
        self.exact_names_suffix = exact_names_suffix
        self.weight = weight
        self.is_italic = is_italic
        self.font_type = font_type
        self.named_instance_coordinates = named_instance_coordinates


    @property
    def families_prefix(self: VariableFont) -> List[Name]:
        return self._families_prefix

    @families_prefix.setter
    def families_prefix(self: VariableFont, value: List[Name]):
        self._families_prefix = value


    @property
    def families_suffix(self: VariableFont) -> List[Name]:
        return self._families_suffix

    @families_suffix.setter
    def families_suffix(self: VariableFont, value: List[Name]):
        self._families_suffix = value


    @property
    def exact_names_suffix(self: VariableFont) -> List[Name]:
        return self._exact_names_suffix

    @exact_names_suffix.setter
    def exact_names_suffix(self: VariableFont, value: List[Name]):
        self._exact_names_suffix = value


    @property
    def named_instance_coordinates(self: VariableFont) -> Dict[str, float]:
        return self._named_instance_coordinates

    @named_instance_coordinates.setter
    def named_instance_coordinates(self: VariableFont, value: Dict[str, float]):
        self._named_instance_coordinates = value


    @property
    def family_names(self: VariableFont) -> List[Name]:
        family_names: List[Name] = []
        for item in product(*[self.families_prefix, self.families_suffix]):
            value = " ".join(element.value for element in item).rstrip(" ")
            # We always use the suffix lang_code. DirectWrite seems to do that.
            # Since GDI doesn't expose the lang_code of an prefix or suffix, there is no way to know how his behaviour.
            lang_code = item[1].lang_code
            family_names.append(Name(value, lang_code))
        return family_names
    
    @family_names.setter
    def family_names(self: VariableFont, value: Any):
        raise AttributeError("You cannot set the family name for an variable font. You need to set the families_prefix or the families_suffix.")

    
    @property
    def exact_names(self: VariableFont) -> List[Name]:
        exact_names: List[Name] = []
        for item in product(*[self.families_prefix, self.exact_names_suffix]):
            value = " ".join(element.value for element in item).rstrip(" ")
            # We always use the suffix lang_code. DirectWrite seems to do that.
            # Since GDI doesn't expose the lang_code of an prefix or suffix, there is no way to know how his behaviour.
            lang_code = item[1].lang_code
            exact_names.append(Name(value, lang_code))
        return exact_names

    @exact_names.setter
    def exact_names(self: VariableFont, value: Any):
        raise AttributeError("You cannot set the exact name for an variable font. You need to set the families_prefix or the exact_names_suffix.")


    @property
    def is_glyph_emboldened(self: VariableFont) -> bool:
        return self.weight > 400

    @is_glyph_emboldened.setter
    def is_glyph_emboldened(self: VariableFont, value: Any):
        raise AttributeError("You cannot set is_glyph_emboldened for an variable font. You need to change the weight.")


    @property
    def named_instance_coordinates(self: VariableFont) -> Dict[str, float]:
        return self._named_instance_coordinates
    
    @named_instance_coordinates.setter
    def named_instance_coordinates(self: VariableFont, value: Dict[str, float]):
        self._named_instance_coordinates = value


    def get_family_prefix_from_lang(self: VariableFont, lang_code: str, exact_match: bool = False) -> List[Name]:
        """
        See the doc of _get_names_from_lang in abc_font
        """
        return self._get_names_from_lang(self.families_prefix, lang_code, exact_match)


    def __eq__(self: VariableFont, other: VariableFont):
        return (self.filename, self.font_index, self.families_prefix, self.families_suffix, self.exact_names_suffix, self.weight, self.is_italic, self.font_type, self.named_instance_coordinates) == (
            other.filename, other.font_index, other.families_prefix, other.families_suffix, other.exact_names_suffix, other.weight, other.is_italic, other.font_type, other.named_instance_coordinates
        )

    def __hash__(self: VariableFont):
        return hash(
            (
                self.filename,
                self.font_index,
                tuple(self.families_prefix),
                tuple(self.families_suffix),
                tuple(self.exact_names_suffix),
                self.weight,
                self.is_italic,
                self.font_type,
                frozenset(self.named_instance_coordinates.items())
            )
        )

    def __repr__(self: VariableFont):
        return f'VariableFont(Filename="{self.filename}", Font index="{self.font_index}", Family_names="{self.family_names}", Exact_names="{self.exact_names}", Weight="{self.weight}", Italic="{self.is_italic}", Glyph emboldened="{self.is_glyph_emboldened}", Font type="{self.font_type.name}", Named instance coordinates="{self.named_instance_coordinates}")'