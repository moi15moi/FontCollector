import os
import sys
from pathlib import Path

from fontTools import ttLib


def main():

    directory = os.getcwd()
    os.makedirs("generated_fonts", exist_ok=True)

    files = [
        Path(os.path.join(directory, f))
        for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f))
    ]

    for file in files:

        try:
            font = ttLib.TTFont(file.name)
        except:
            continue

        font["name"].setName("Raleway", 1, 3, 1, 0x409)

        font.save(f"generated_fonts/{file.name} - generated.ttf")


if __name__ == "__main__":
    sys.exit(main())
