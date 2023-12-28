from __future__ import annotations
from collections import Counter
from .factory_abc_font_face import FactoryABCFontFace
from os import PathLike
from os.path import realpath
from time import time
from typing import Iterable, TYPE_CHECKING, List

if TYPE_CHECKING:
    from .abc_font_face import ABCFontFace


class FontFile:

    def __init__(
        self: FontFile,
        filename: PathLike[str],
        font_faces: Iterable[ABCFontFace],
        last_loaded_time: float = time()
    ) -> FontFile:
        self.__filename = realpath(filename)
        self.__font_faces = list(font_faces)
        for font_face in self.__font_faces:
            font_face.link_face_to_a_font_file(self)
        self.__last_loaded_time = last_loaded_time

    @property
    def filename(self: FontFile) -> PathLike[str]:
        return self.__filename

    @property
    def font_faces(self: FontFile) -> List[ABCFontFace]:
        return self.__font_faces

    @property
    def last_loaded_time(self: FontFile) -> float:
        return self.__last_loaded_time

    @classmethod
    def from_font_path(cls: FontFile, filename: PathLike[str]) -> FontFile:
        font_faces = FactoryABCFontFace.from_font_path(filename)
        return cls(filename, font_faces)

    def reload_font_file(self: FontFile):
        self.__font_faces = FactoryABCFontFace.from_font_path(self.filename)
        for font_face in self.__font_faces:
            font_face.font_file = self
        self.__last_loaded_time = time()

    def __eq__(self: FontFile, other: FontFile) -> bool:
        return (self.filename, self.last_loaded_time) == (
            other.filename, other.last_loaded_time
        ) and Counter(self.font_faces) == Counter(other.font_faces)

    def __hash__(self: FontFile) -> int:
        return hash(
            (
                self.filename,
                self.font_faces,
                self.last_loaded_time,
            )
        )


    def __repr__(self: FontFile) -> str:
        return f'{self.__class__.__name__}(Filename="{self.filename}", Font faces="{self.font_faces}", Last loaded time="{self.last_loaded_time}"'
