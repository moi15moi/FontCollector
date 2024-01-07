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

    def __init__(
        self: FontFile,
        filename: Path,
        font_faces: List[ABCFontFace],
        last_loaded_time: Optional[float] = None
    ) -> None:
        if not isfile(filename):
            raise FileNotFoundError(f'The file "{filename}" doesn\'t exist.')
        if len(font_faces) == 0:
            raise ValueError(f"A FontFile need to contain at least 1 ABCFontFace.")
        self.__filename = filename
        self.__font_faces = font_faces
        for font_face in self.__font_faces:
            font_face.link_face_to_a_font_file(self)

        if last_loaded_time is None:
            self.__last_loaded_time = time()
        else:
            self.__last_loaded_time = last_loaded_time

    @property
    def filename(self: FontFile) -> Path:
        return self.__filename

    @property
    def font_faces(self: FontFile) -> List[ABCFontFace]:
        return self.__font_faces

    @property
    def last_loaded_time(self: FontFile) -> float:
        return self.__last_loaded_time

    @classmethod
    def from_font_path(cls: Type[FontFile], filename: Path) -> FontFile:
        font_faces = FactoryABCFontFace.from_font_path(filename)
        return cls(filename, font_faces)

    def reload_font_file(self: FontFile) -> None:
        self.__font_faces = FactoryABCFontFace.from_font_path(self.filename)
        for font_face in self.__font_faces:
            font_face.link_face_to_a_font_file(self)
        self.__last_loaded_time = time()

    def __eq__(self: FontFile, other: object) -> bool:
        if not isinstance(other, FontFile):
            return False
        return self.filename == other.filename and Counter(self.font_faces) == Counter(other.font_faces)

    def __hash__(self: FontFile) -> int:
        return hash(
            (
                self.filename,
                frozenset(self.font_faces),
            )
        )

    def __repr__(self: FontFile) -> str:
        return f'{self.__class__.__name__}(Filename="{self.filename}", Font faces="{self.font_faces}", Last loaded time="{self.last_loaded_time}")'
