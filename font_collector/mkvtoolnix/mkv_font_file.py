from pathlib import Path

__all__ = ["MKVFontFile"]

class MKVFontFile:

    def __init__(self, filename: Path, mkv_id: int, font_filename: str) -> None:
        self.filename = filename
        self.mkv_id = mkv_id
        self.mkv_font_filename = font_filename

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(Filename="{self.filename}", MKV ID="{self.mkv_id}", MKV attachment filename="{self.mkv_font_filename}")'
