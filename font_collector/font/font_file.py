from __future__ import annotations
from .factory_abc_font_face import FactoryABCFontFace
from collections import Counter
from os.path import isfile, realpath
from pathlib import Path
from time import time
from typing import List, Optional, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from .abc_font_face import ABCFontFace

__all__ = ["FontFile"]

class FontFile:
    """Represents a physical font file.

    Attributes:
        filename: The name of the font file.
        font_faces: A list of FontFace objects associated with the font file.
        last_loaded_time: The timestamp, in seconds since the Epoch, when the font file was last loaded.
    """

    def __init__(
        self,
        filename: Path,
        font_faces: List[ABCFontFace],
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
        if not isfile(filename):
            raise FileNotFoundError(f'The file "{filename}" doesn\'t exist.')
        if len(font_faces) == 0:
            raise ValueError(f"A FontFile need to contain at least 1 ABCFontFace.")
        self.__filename = filename
        self.__font_faces = font_faces
        for font_face in self.font_faces:
            font_face.link_face_to_a_font_file(self)

        if last_loaded_time is None:
            self.__last_loaded_time = time()
        else:
            self.__last_loaded_time = last_loaded_time

    @property
    def filename(self) -> Path:
        return self.__filename

    @property
    def font_faces(self) -> List[ABCFontFace]:
        return self.__font_faces

    @property
    def last_loaded_time(self) -> float:
        return self.__last_loaded_time

    @classmethod
    def from_font_path(cls: Type[FontFile], filename: Path) -> FontFile:
        font_faces = FactoryABCFontFace.from_font_path(filename)
        return cls(filename, font_faces)

    def reload_font_file(self) -> None:
        """
        Reloads the font file to update the font faces.
        """
        self.__font_faces = FactoryABCFontFace.from_font_path(self.filename)
        for font_face in self.__font_faces:
            font_face.link_face_to_a_font_file(self)
        self.__last_loaded_time = time()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FontFile):
            return False
        return self.filename == other.filename and Counter(self.font_faces) == Counter(other.font_faces)

    def __hash__(self) -> int:
        return hash(
            (
                self.filename,
                frozenset(self.font_faces),
            )
        )

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(Filename="{self.filename}", Font faces="{self.font_faces}", Last loaded time="{self.last_loaded_time}")'
