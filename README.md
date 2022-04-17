# FontCollector
FontCollector for Advanced SubStation Alpha file.
## Installation
```text
pip install git+https://github.com/moi15moi/FontCollector.git
```

## Usage

```text
$ fontCollector --help
usage: fontCollector.py [-h] --input <.ass file> [-mkv .mkv input file] [--output [path]] [-mkvmerge path]

FontCollector for Advanced SubStation Alpha file.

optional arguments:
  -h, --help            				show this help message and exit
  --input <.ass file>, -i <.ass file>	Subtitles file. Must be an ASS file.
  -mkv .mkv input file  				Video where the fonts will be merge. Must be a Matroska file.
  --output [path], -o [path]			Destination path of the font. If not specified, it will be the current path.
  -mkvmerge path        				Path to mkvmerge.exe if not in variable environments.
```

## Know issues
Currently, FontCollector can't collect font if the fontName contains Japanese or Chinese characters.

## Acknowledgments
 - [Myaamori-Aegisub-Scripts](https://github.com/TypesettingTools/Myaamori-Aegisub-Scripts)
 - [fontmerge](https://github.com/WheneverDev/fontmerge)
