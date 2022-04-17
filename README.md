# FontCollector
FontCollector for Advanced SubStation Alpha file.
## Installation
```text
pip install git+https://github.com/moi15moi/FontCollector.git
```

## Usage

```text
$ fontCollector --help
usage: fontCollector.py [-h] --input <.ass file> [-mkv .mkv input file] [--output [path]] [-mkvpropedit path] [--delete-fonts]
FontCollector for Advanced SubStation Alpha file.

required argument:
  --input <.ass file>, -i <.ass file>
	Subtitles file. Must be an ASS file.

optional arguments:
  -h, --help            
	show this help message and exit
  -mkv .mkv input file  
	Video where the fonts will be merge. Must be a Matroska file.
  --output [path], -o [path]
	Destination path of the font. If not specified, it will be the current path.
  -mkvpropedit path     
	Path to mkvpropedit.exe if not in variable environments. If -mkv is not specified, it will do nothing.
  --delete-fonts, -d    
	If -d is specified, it will delete the font attached to the mkv before merging the new needed font. If -mkv is not specified, it will do nothing.
```

## Know issues
Currently, FontCollector can't collect font if the fontName contains Japanese or Chinese characters.

## Acknowledgments
 - [Myaamori-Aegisub-Scripts](https://github.com/TypesettingTools/Myaamori-Aegisub-Scripts)
 - [fontmerge](https://github.com/WheneverDev/fontmerge)
