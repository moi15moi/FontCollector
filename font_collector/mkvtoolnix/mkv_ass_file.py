from .auto_delete_path import AutoDeletePath
from typing import List
from ..font.font_file import FontFile

__all__ = ["MKVASSFile"]

class MKVASSFile:

    def __init__(self, filename: AutoDeletePath, mkv_id: int) -> None:
        self.filename = filename
        self.mkv_id = mkv_id
