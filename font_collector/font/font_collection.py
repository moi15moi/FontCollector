from __future__ import annotations
from ..ass.ass_style import AssStyle
from .abc_font_face import ABCFontFace, FontType
from .font_file import FontFile
from .font_loader import FontLoader
from .font_result import FontResult
from os.path import getctime
from typing import Any, Iterable, List, Optional, Set


class FontCollection:
    """Contains fonts. This class allows to query fonts.

    Attributes:
        use_system_font (bool): If true, then the collection will contains the system font.
        reload_system_font (bool): If true, then each time you will try to access the system_fonts,
            it will reload it to see if any new font(s) have been installed or uninstalled. This can reduce performance.
            If false, it will only load the system font 1 time and never reload it.
        use_generated_fonts (bool): Use the cached font collection (.ttc file) that were been generated from an variable font.
        system_fonts (Set[ABCFont]): If use_system_font is set to True, it will contain the system font. 
            If false, it will be empty.
        generated_fonts (Set[ABCFont]): It use_generated_fonts is set to True, it will contain the font collection (.ttc file) that were been generated from an variable font. 
            If false, it will be empty.
            Warning: All the FontCollection use the same generated_fonts.
        additional_fonts (Set[ABCFont]): It contain the font you specified.
        fonts (Set[ABCFont]): It contain the font(s) from system_fonts, generated_fonts and additional_fonts.
    """


    def __init__(
        self: FontCollection, 
        use_system_font: bool = True,
        reload_system_font: bool = False,
        use_generated_fonts: bool = True,
        additional_fonts: List[FontFile] = [], 
    ) -> FontCollection:
        self.use_system_font = use_system_font
        self.reload_system_font = reload_system_font
        self.use_generated_fonts = use_generated_fonts
        self.additional_fonts = additional_fonts

    
    def __iter__(self: FontCollection) -> FontFile:
        for font in self.fonts:
            yield font


    @property
    def system_fonts(self: FontCollection) -> List[FontFile]:
        if self.use_system_font:
            if self.reload_system_font:
                return FontLoader.load_system_fonts()

            if not hasattr(self, '__system_fonts'):
                self.__system_fonts = FontLoader.load_system_fonts()
            return self.__system_fonts
        return []

    @system_fonts.setter
    def system_fonts(self: FontCollection, value: Any):
        raise AttributeError("You cannot set system_fonts, but you can set use_system_font")


    @property
    def generated_fonts(self: FontCollection) -> List[FontFile]:
        if self.use_generated_fonts:
            return FontLoader.load_generated_fonts()
        return []

    @generated_fonts.setter
    def generated_fonts(self: FontCollection, value: Any):
        raise AttributeError("You cannot set generated_fonts, but you can set use_generated_fonts")


    @property
    def fonts(self: FontCollection) -> List[FontFile]:
        return self.system_fonts + self.generated_fonts + self.additional_fonts

    @fonts.setter
    def fonts(self: FontCollection, value: Any):
        raise AttributeError("You cannot set the fonts. If you want to add font, set additional_fonts")


    def get_used_font_by_style(self: FontCollection, style: AssStyle) -> Optional[FontResult]:
        """
        Parameters:
            style (AssStyle): An AssStyle
        Returns:
            The best font that match an AssStyle.
            The algorithm is based on GDI.
            If no font are found, then it return None.
        """

        score_min = float('inf')
        selected_font_face: Optional[ABCFontFace] = None
        for font_file in self.fonts:
            for font_face in font_file.font_faces:
                score = float('inf')
                exact_name_match = False

                family_name_match = any(style.fontname.lower() == family_name.value.lower() for family_name in font_face.family_names)

                if family_name_match:
                    score = font_face.get_similarity_score(style)
                else:
                    exact_name_match = any(style.fontname.lower() == exact_name.value.lower() for exact_name in font_face.exact_names)
                    if exact_name_match:
                        score = font_face.get_similarity_score(style)
                
                if family_name_match or exact_name_match:
                    if score < score_min:
                        score_min = score
                        selected_font_face = font_face
                    elif score == score_min:
                        # GDI prefers the oldest font when the score between 2 fonts is exactly the same.
                        # However, for us, it is impossible to know when a font has been installed. 
                        # GDI, DirectWrite, CoreText and Fontconfig don't offer a way to retrieve the installation date of a font.
                        # So, we get the creation date of the font, which should be the same as when it has been installed.
                        # But, there is an exception:
                        #   On Windows, if the user has called AddFontResourceW to install a font, the creation date of the file is not the same as when it has been installed.
                        #   On macOS, the same problem occurs with CTFontManagerRegisterFontsForURL.
                        # But, this use case is really rare, so it is almost impossible to happen and anyways, there is nothing we can do to avoid it.
                        #if selected_font is None or getctime(font.filename) < getctime(selected_font.filename):
                        if getctime(font_face.font_file.filename) < getctime(selected_font_face.font_file.filename):
                            selected_font_face = font_face

        if selected_font_face is None:
            return None

        need_faux_bold = selected_font_face.need_faux_bold(style.weight)
        mismatch_bold = abs(selected_font_face.weight - style.weight) >= 150
        mismatch_italic = selected_font_face.is_italic != style.italic

        font_result = FontResult(selected_font_face, mismatch_bold, need_faux_bold, mismatch_italic)
        return font_result
    

    def __eq__(self: FontCollection, other: FontCollection) -> bool:
        return (self.use_system_font, self.reload_system_font, self.use_generated_fonts, self.additional_fonts) == (
            other.use_system_font, other.reload_system_font, other.use_generated_fonts, other.additional_fonts
        )

    def __hash__(self: FontCollection) -> int:
        return hash(
            (
                self.use_system_font,
                self.reload_system_font,
                self.use_generated_fonts,
                frozenset(self.additional_fonts),
            )
        )

    def __repr__(self: FontCollection) -> str:
        return f'{self.__class__.__name__}(Use system font="{self.use_system_font}", Reload system font="{self.reload_system_font}", Use generated fonts="{self.use_generated_fonts}", Additional fonts="{self.additional_fonts}")'
