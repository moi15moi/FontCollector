from pathlib import Path

__all__ = ["AutoDeletePath"]

class AutoDeletePath:
    def __init__(self, *args, **kwargs):
        self.path = Path(*args, **kwargs)

    def __del__(self):
        if self.path.exists():
            self.path.unlink()