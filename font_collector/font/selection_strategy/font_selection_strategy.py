from abc import ABC, abstractmethod

from ...ass.ass_style import AssStyle
from ..abc_font_face import ABCFontFace

__all__ = ["FontSelectionStrategy"]

class FontSelectionStrategy(ABC):
    """
    The FontSelectionStrategy class defines the Strategy interface for selecting fonts
    based on specific algorithms. Concrete implementations of this interface provide
    strategies for determining whether a font needs faux bold and calculating a similarity
    score between a font face and an AssStyle.
    """

    @abstractmethod
    def is_font_name_match(self, font_face: ABCFontFace, style_font_name: str) -> bool:
        """
        Args:
            font_face: A FontFace
            style_font_name: A font name. It can come from a AssStyle
        Returns:
            True if the style_font_name match with the font_face. Otherwise, False.
        """


    @abstractmethod
    def need_faux_bold(self, font_face: ABCFontFace, style: AssStyle) -> bool:
        """
        Args:
            font_face: A FontFace
            style: An AssStyle
        Returns:
            True if the font face needs to have faux bold to display like the AssStyle, otherwise, false.
        """


    @abstractmethod
    def get_similarity_score(self, font_face: ABCFontFace, style: AssStyle) -> float:
        """
        Args:
            font_face: A FontFace
            style: An AssStyle
        Returns:
            A matching score between the font_face and the style.
            The lower, the better. If it returns 0, it means it is a perfect match.
            If it returns infinity, then the font name between the style and the font face doesn't match.
        """
