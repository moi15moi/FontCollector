# FontCollector
FontCollector for Advanced SubStation Alpha file.
## Installation
```text
pip install git+https://github.com/moi15moi/FontCollector.git
```

## Usage

```text
$ fontCollector --help
usage: fontCollector [-h] [--input file] [--output path]

FontCollector for Advanced SubStation Alpha file.

optional arguments:
  -h, --help            	show this help message and exit
  --input file, -i file		Subtitles file. Must be an ASS file.
  --output path, -o path	Destination path of the font
```

## Know issues
Currently, FontCollector can't collect font if the fontName contains Japanese or Chinese characters.
