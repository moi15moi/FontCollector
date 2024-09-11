from .auto_delete_path import AutoDeletePath
from typing import List
from ..font.font_file import FontFile

__all__ = ["MKVFontFile"]

class MKVFontFile:

    def __init__(self, filename: AutoDeletePath, mkv_id: int, mkv_filename: str) -> None:
        self.filename = filename
        self.mkv_id = mkv_id
        self.mkv_filename = mkv_filename
