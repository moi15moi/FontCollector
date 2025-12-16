from pathlib import Path

__all__ = ["MKVASSFile"]

class MKVASSFile:

    def __init__(self, filename: Path, mkv_id: int, track_name: str | None) -> None:
        self.filename = filename
        self.mkv_id = mkv_id
        self.track_name = track_name

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(Filename="{self.filename}", MKV ID="{self.mkv_id}", Track name="{self.track_name}")'
