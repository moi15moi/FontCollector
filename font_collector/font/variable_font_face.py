from __future__ import annotations
from ..exceptions import InvalidVariableFontFaceException
from .._version import __version__
from .abc_font_face import ABCFontFace
from .name import Name, NameID
from .font_parser import FontParser
from .font_type import FontType
from datetime import date
from fontTools.ttLib.ttCollection import TTCollection
from fontTools.ttLib.ttFont import TTFont
from fontTools.varLib import instancer
from itertools import product
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from . import FontFile

__all__ = ["VariableFontFace"]

class VariableFontFace(ABCFontFace):
    """Represents a variable font face of a font file.
    A variable font face is a face where the glyph can have variations along certain axes.
    For more detail about variable font, see: https://learn.microsoft.com/en-us/typography/opentype/spec/otvaroverview

    For the list of Attributes, see the doc of: ABCFontFace
    But, this class also has some specific attribute:
        families_prefix: This is the equivalent of family_names for NormalFontFace. ex: "Alegreya"
        families_suffix: The family_names suffix. ex: "Medium"
        exact_names_suffix: The exact_names suffix. ex: "Medium Italic"
        named_instance_coordinates: The value of each AxisTag ex: {"wght": 800.0}
            For more detail, see: https://learn.microsoft.com/en-us/typography/opentype/spec/fvar#instancerecord
    """

    def __init__(
        self,
        font_index: int,
        families_prefix: List[Name],
        families_suffix: List[Name],
        exact_names_suffix: List[Name],
        weight: int,
        is_italic: bool,
        font_type: FontType,
        named_instance_coordinates: Dict[str, float],
    ) -> None:
        if len(families_prefix) == 0:
            raise InvalidVariableFontFaceException("The font does not contain an valid family prefix.")

        self.__font_index = font_index
        self.__families_prefix = families_prefix
        self.__families_suffix = families_suffix
        self.__exact_names_suffix = exact_names_suffix
        self.__weight = weight
        self.__is_italic = is_italic
        self.__font_type = font_type
        self.__named_instance_coordinates = named_instance_coordinates
        self.__font_file = None


    @property
    def font_index(self) -> int:
        return self.__font_index

    @property
    def family_names(self) -> List[Name]:
        """
        Computed property that generates a list of family names based on families_prefix and families_suffix
        """
        family_names: List[Name] = []
        if len(self.families_suffix) == 0:
            family_names = self.families_prefix
        else:
            for item in product(*[self.families_prefix, self.families_suffix]):
                value = " ".join(element.value for element in item).rstrip(" ")
                # We always use the suffix lang_code. DirectWrite seems to do that.
                # Since GDI doesn't expose the lang_code of an prefix or suffix, there is no way to know how his behaviour.
                lang_code = item[1].lang_code
                family_names.append(Name(value, lang_code))
        return family_names

    @family_names.setter
    def family_names(self, value: Any) -> None:
        raise AttributeError("You cannot set the family name for an variable font. It is automatically generated by the families_prefix and the families_suffix.")

    @property
    def exact_names(self) -> List[Name]:
        """
        Computed property that generates a list of family names based on families_prefix and exact_names_suffix
        """
        exact_names: List[Name] = []
        for item in product(*[self.families_prefix, self.exact_names_suffix]):
            value = " ".join(element.value for element in item).rstrip(" ")
            # We always use the suffix lang_code. DirectWrite seems to do that.
            # Since GDI doesn't expose the lang_code of an prefix or suffix, there is no way to know how his behaviour.
            lang_code = item[1].lang_code
            exact_names.append(Name(value, lang_code))
        return exact_names

    @exact_names.setter
    def exact_names(self, value: Any) -> None:
        raise AttributeError("You cannot set the exact name for an variable font. It is automatically generated by the families_prefix and the exact_names_suffix.")

    @property
    def weight(self) -> int:
        return self.__weight

    @property
    def is_italic(self) -> bool:
        return self.__is_italic

    @property
    def is_glyph_emboldened(self) -> bool:
        return self.weight > 400

    @is_glyph_emboldened.setter
    def is_glyph_emboldened(self, value: Any) -> None:
        raise AttributeError("You cannot set is_glyph_emboldened for an variable font. It is automatically generated by the weight.")

    @property
    def font_type(self) -> FontType:
        return self.__font_type

    @property
    def font_file(self) -> Optional[FontFile]:
        return self.__font_file

    def link_face_to_a_font_file(self, value: FontFile) -> None:
        # Since there is a circular reference between FontFile and this class, we need to be able to set the value
        self.__font_file = value

    @property
    def families_prefix(self) -> List[Name]:
        return self.__families_prefix

    @property
    def families_suffix(self) -> List[Name]:
        return self.__families_suffix

    @property
    def exact_names_suffix(self) -> List[Name]:
        return self.__exact_names_suffix

    @property
    def named_instance_coordinates(self) -> Dict[str, float]:
        return self.__named_instance_coordinates


    def get_family_prefix_from_lang(self, lang_code: str, exact_match: bool = False) -> Optional[Name]:
        """
        See the doc of _get_name_from_lang in abc_font
        """
        return self._get_name_from_lang(self.families_prefix, lang_code, exact_match)


    def get_best_family_prefix_from_lang(self) -> Name:
        """
        See the doc of _get_best_name
        """
        return self._get_best_name(self.families_prefix)


    def variable_font_to_collection(self, save_path: Path, cache_generated_font: bool = True) -> FontFile:
        """
        Args:
            save_path: Path where to save the generated font
            cache_generated_font: Converting an variable font into an collection font is a slow process. Caching the result boost the performance.
                If true, then the generated font will be cached.
                If false, then the generated font won't be cached.
        Returns:
            List of Font that represent the truetype collection font generated
        """
        if self.font_file is None:
            raise ValueError("This font_face isn't linked to any FontFile.")

        if save_path.is_file():
            raise FileExistsError(f'There is already a font at "{save_path}"')

        font_collection = TTCollection()
        ttFont = TTFont(self.font_file.filename, fontNumber=self.font_index)

        # Only conserve the right font_index
        fonts_face: List[VariableFontFace] = [
            font for font in self.font_file.font_faces
            if font.font_index == self.font_index and isinstance(font, VariableFontFace)
        ]

        if len(fonts_face) == 0:
            raise ValueError(f"There is no valid font at the index {self.font_index}")

        cmaps = FontParser.get_supported_cmaps(ttFont)

        for font_face in fonts_face:
            generated_font_face = instancer.instantiateVariableFont(ttFont, font_face.named_instance_coordinates)

            for cmap in cmaps:
                for family_name in font_face.family_names:
                    generated_font_face["name"].setName(family_name.value, NameID.FAMILY_NAME, cmap.platform_id, cmap.platform_enc_id, family_name.get_lang_id_from_platform_id(cmap.platform_id))

                for exact_name in font_face.exact_names:
                    generated_font_face["name"].setName(exact_name.value, NameID.FULL_NAME, cmap.platform_id, cmap.platform_enc_id, exact_name.get_lang_id_from_platform_id(cmap.platform_id))
                    generated_font_face["name"].setName(exact_name.value, NameID.POSTSCRIPT_NAME, cmap.platform_id, cmap.platform_enc_id, exact_name.get_lang_id_from_platform_id(cmap.platform_id))
                    generated_font_face["name"].setName(exact_name.value, NameID.SUBFAMILY_NAME, cmap.platform_id, cmap.platform_enc_id, exact_name.get_lang_id_from_platform_id(cmap.platform_id))

                    generated_font_face["name"].setName(
                        f"FontCollector v {__version__}:{exact_name.value}:{date.today()}",
                        NameID.UNIQUE_ID,
                        cmap.platform_id,
                        cmap.platform_enc_id,
                        exact_name.get_lang_id_from_platform_id(cmap.platform_id),
                    )

            selection = generated_font_face["OS/2"].fsSelection
            # First clear...
            selection &= ~(1 << 0)
            selection &= ~(1 << 5)
            selection &= ~(1 << 6)
            # ...then re-set the bits.
            if font_face.named_instance_coordinates.get("wght", 0) == 400.0:
                selection |= 1 << 6
            if font_face.named_instance_coordinates.get("ital", 0) == 1:
                selection |= 1 << 0
            if font_face.named_instance_coordinates.get("wght", 0) > 400.0:
                selection |= 1 << 5
            generated_font_face["OS/2"].fsSelection = selection

            font_collection.fonts.append(generated_font_face)

        font_collection.save(save_path)
        from .font_file import FontFile
        generated_font = FontFile.from_font_path(save_path)

        if cache_generated_font:
            from .font_loader import FontLoader
            FontLoader.add_generated_font(generated_font)

        return generated_font


    def __eq__(self, other: object) -> bool:
        if not isinstance(other, VariableFontFace):
            return False
        return (self.font_index, self.families_prefix, self.families_suffix, self.exact_names_suffix, self.weight, self.is_italic, self.font_type, self.named_instance_coordinates) == (
            other.font_index, other.families_prefix, other.families_suffix, other.exact_names_suffix, other.weight, other.is_italic, other.font_type, other.named_instance_coordinates
        )


    def __hash__(self) -> int:
        return hash(
            (
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


    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(Font index="{self.font_index}", Family names="{self.family_names}", Exact names="{self.exact_names}", Weight="{self.weight}", Italic="{self.is_italic}", Glyph emboldened="{self.is_glyph_emboldened}", Font type="{self.font_type.name}", Named instance coordinates="{self.named_instance_coordinates}")'