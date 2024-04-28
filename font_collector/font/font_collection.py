from __future__ import annotations
from collections import Counter
from ..ass import AssStyle
from .abc_font_face import ABCFontFace
from .font_file import FontFile
from .font_loader import FontLoader
from .font_result import FontResult
from .selection_strategy import FontSelectionStrategy
from typing import Any, Generator, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .abc_font_face import ABCFontFace
    from .font_file import FontFile

__all__ = ["FontCollection"]

class FontCollection:
    """A collection of fonts. This class allows querying fonts.

    Attributes:
        use_system_font: If True, then the collection will contain the system font.
        reload_system_font: If True, each time you access the system_fonts,
            it will reload to check for any newly installed or uninstalled fonts. This may impact performance.
            If False, it will load the system font only once and never reload it.
        use_generated_fonts: Use the cached font collection (.ttc file) generated from a variable font.
        system_fonts: If use_system_font is set to True, it will contain the system font.
            If False, it will be empty.
        generated_fonts: If use_generated_fonts is set to True, it will contain the font collection (.ttc file) generated from a variable font.
            If False, it will be empty.
            Warning: All FontCollections use the same generated_fonts.
        additional_fonts: Contains the specified additional fonts.
        fonts: A list that contain `system_fonts`, `generated_fonts`, and `additional_fonts`.
    """

    def __init__(
        self,
        use_system_font: bool = True,
        reload_system_font: bool = False,
        use_generated_fonts: bool = True,
        additional_fonts: List[FontFile] = [],
    ) -> None:
        self.use_system_font = use_system_font
        self.reload_system_font = reload_system_font
        self.use_generated_fonts = use_generated_fonts
        self.additional_fonts = additional_fonts


    def __iter__(self) -> Generator[FontFile, None, None]:
        for font in self.fonts:
            yield font


    @property
    def system_fonts(self) -> List[FontFile]:
        if self.use_system_font:
            if self.reload_system_font:
                return FontLoader.load_system_fonts()

            if not hasattr(self, '__system_fonts'):
                self.__system_fonts = FontLoader.load_system_fonts()
            return self.__system_fonts
        return []

    @system_fonts.setter
    def system_fonts(self, value: Any) -> None:
        raise AttributeError("You cannot set system_fonts, but you can set use_system_font")


    @property
    def generated_fonts(self) -> List[FontFile]:
        if self.use_generated_fonts:
            return FontLoader.load_generated_fonts()
        return []

    @generated_fonts.setter
    def generated_fonts(self, value: Any) -> None:
        raise AttributeError("You cannot set generated_fonts, but you can set use_generated_fonts")


    @property
    def fonts(self) -> List[FontFile]:
        return self.system_fonts + self.generated_fonts + self.additional_fonts

    @fonts.setter
    def fonts(self, value: Any) -> None:
        raise AttributeError("You cannot set the fonts. If you want to add font, set additional_fonts")


    def get_used_font_by_style(self, style: AssStyle, strategy: FontSelectionStrategy) -> Optional[FontResult]:
        """
        Args:
            style: An AssStyle
            strategy: The strategy used to select the best font face that corresponds to the style.
        Returns:
            The best font that matches an AssStyle based on the strategy algorithm.
            If no fonts are found, it returns None.
        """
        score_min = float('inf')
        selected_font_face: Optional[ABCFontFace] = None
        for font_file in self.fonts:
            for font_face in font_file.font_faces:
                score = strategy.get_similarity_score(font_face, style)

                if score < float("inf"):
                    if selected_font_face is None:
                        score_min = score
                        selected_font_face = font_face
                    elif score < score_min:
                        score_min = score
                        selected_font_face = font_face
                    elif score == score_min:
                        if font_face.font_file is None:
                            raise ValueError(f"The font_face \"{font_face}\" isn't linked to any FontFile.")
                        if selected_font_face.font_file is None:
                            raise ValueError(f"The selected_font_face \"{selected_font_face}\" isn't linked to any FontFile.")
                        # GDI prefers the oldest font when the score between 2 fonts is exactly the same.
                        # However, for us, it is impossible to know when a font has been installed.
                        # GDI, DirectWrite, CoreText and Fontconfig don't offer a way to retrieve the installation date of a font.
                        # So, we get the creation date of the font, which should be the same as when it has been installed.
                        # But, there is an exception:
                        #   On Windows, if the user has called AddFontResourceW to install a font, the creation date of the file is not the same as when it has been installed.
                        #   On macOS, the same problem occurs with CTFontManagerRegisterFontsForURL.
                        # But, this use case is really rare, so it is almost impossible to happen and anyways, there is nothing we can do to avoid it.
                        if font_face.font_file.filename.stat().st_ctime < selected_font_face.font_file.filename.stat().st_ctime:
                            selected_font_face = font_face

        if selected_font_face is None:
            return None

        need_faux_bold = strategy.need_faux_bold(selected_font_face, style)
        mismatch_bold = abs(selected_font_face.weight - style.weight) >= 150
        mismatch_italic = selected_font_face.is_italic != style.italic

        font_result = FontResult(selected_font_face, mismatch_bold, need_faux_bold, mismatch_italic)
        return font_result


    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FontCollection):
            return False
        return (self.use_system_font, self.reload_system_font, self.use_generated_fonts) == (
            other.use_system_font, other.reload_system_font, other.use_generated_fonts
        ) and Counter(self.additional_fonts) == Counter(other.additional_fonts)


    def __hash__(self) -> int:
        return hash(
            (
                self.use_system_font,
                self.reload_system_font,
                self.use_generated_fonts,
                frozenset(self.additional_fonts),
            )
        )

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(Use system font="{self.use_system_font}", Reload system font="{self.reload_system_font}", Use generated fonts="{self.use_generated_fonts}", Additional fonts="{self.additional_fonts}")'
