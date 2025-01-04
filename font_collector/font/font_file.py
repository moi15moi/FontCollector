from __future__ import annotations
from .factory_abc_font_face import FactoryABCFontFace
from collections import Counter
from pathlib import Path
from time import time
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .abc_font_face import ABCFontFace

__all__ = ["FontFile"]

class FontFile:
    """Represents a physical font file.

    Attributes:
        filename: The name of the font file.
        font_faces: A list of FontFace objects associated with the font file.
        is_collection_font: True if the FontFile represent a TTC or OTC font, otherwhise, False.
        last_loaded_time: The timestamp, in seconds since the Epoch, when the font file was last loaded.
    """

    def __init__(
        self,
        filename: Path,
        font_faces: list[ABCFontFace],
        is_collection_font: bool,
        last_loaded_time: Optional[float] = None
    ) -> None:
        """Initializes the FontFile instance.

        It links the font faces to this newly created FontFile instance.

        Args:
            filename: The name of the font file.
            font_faces: A list of FontFace objects associated with the font file.
            last_loaded_time: The timestamp, in seconds since the Epoch, when the font file was last loaded.
                If None, it will be set to the current time.
        """
        if not filename.is_file():
            raise FileNotFoundError(f'The file "{filename}" doesn\'t exist.')
        if len(font_faces) == 0:
            raise ValueError(f"A FontFile need to contain at least 1 ABCFontFace.")
        self.__filename = filename
        self.__font_faces = font_faces
        for font_face in self.font_faces:
            font_face.link_face_to_a_font_file(self)

        self.__is_collection_font = is_collection_font

        if last_loaded_time is None:
            self.__last_loaded_time = time()
        else:
            self.__last_loaded_time = last_loaded_time

    @property
    def filename(self) -> Path:
        return self.__filename

    @property
    def font_faces(self) -> list[ABCFontFace]:
        return self.__font_faces

    @property
    def is_collection_font(self) -> bool:
        return self.__is_collection_font

    @property
    def last_loaded_time(self) -> float:
        return self.__last_loaded_time

    @classmethod
    def from_font_path(cls: type[FontFile], filename: Path) -> FontFile:
        font_faces, is_collection_font = FactoryABCFontFace.from_font_path(filename)
        return cls(filename, font_faces, is_collection_font)

    def reload_font_file(self) -> None:
        """
        Reloads the font file to update the font faces.
        """
        self.__font_faces, self.__is_collection_font = FactoryABCFontFace.from_font_path(self.filename)
        for font_face in self.__font_faces:
            font_face.link_face_to_a_font_file(self)
        self.__last_loaded_time = time()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FontFile):
            return False
        return self.filename == other.filename and Counter(self.font_faces) == Counter(other.font_faces) and self.is_collection_font == other.is_collection_font

    def __hash__(self) -> int:
        return hash(
            (
                self.filename,
                frozenset(self.font_faces),
                self.is_collection_font,
            )
        )

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(Filename="{self.filename}", Font faces="{self.font_faces}", Is collection Font="{self.is_collection_font}", Last loaded time="{self.last_loaded_time}")'
