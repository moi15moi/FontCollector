# FontCollector
FontCollector for Advanced SubStation Alpha file.
## Installation
```text
pip install git+https://github.com/moi15moi/FontCollector.git
```

## Usage

```text
$ fontCollector --help
usage: fontCollector.py [-h] [--output path] <Ass file>

FontCollector for Advanced SubStation Alpha file.

positional arguments:
  <Ass file>                Subtitles file. Must be an ASS file.

optional arguments:
  -h, --help                show this help message and exit
  --output path, -o path    Destination path of the font. If not specified, it will be the current path.
```

## Know issues
Currently, FontCollector can't collect font if the fontName contains Japanese or Chinese characters.
