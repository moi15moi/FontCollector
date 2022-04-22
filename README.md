# FontCollector
FontCollector for Advanced SubStation Alpha file.
## Installation
```text
pip install git+https://github.com/moi15moi/FontCollector.git
```

## Usage

```text
$ fontCollector --help
usage: fontCollector.py [-h] --input [.ass file] [[.ass file] ...] [-mkv [.mkv input file]] [--output [path]]
                        [-mkvpropedit [path]] [--delete-fonts] [--additional-fonts [path [path ...]]]

FontCollector for Advanced SubStation Alpha file.

optional arguments:
  -h, --help            
		show this help message and exit
  --input [.ass file] [[.ass file] ...], -i [.ass file] [[.ass file] ...]
		Subtitles file. Must be an ASS file. You can specify more than one .ass file.
  -mkv [.mkv input file]
		Video where the fonts will be merge. Must be a Matroska file.
  --output [path], -o [path]
		Destination path of the font. If not specified, it will be the current path.
  -mkvpropedit [path]   
		Path to mkvpropedit.exe if not in variable environments. If -mkv is not specified, it will do nothing.
  --delete-fonts, -d    
		If -d is specified, it will delete the font attached to the mkv before merging the new needed font. 
		If -mkv is not specified, it will do nothing.
  --additional-fonts [path [path ...]]
		May be a directory containing font files or a single font file. You can specify more than one additional-fonts.
```

## Know issues
Currently, FontCollector does not always collect font when the font is Japanese or Chinese. It seems to be a problem from [FontTools](https://github.com/fonttools/fonttools) that do not decode the fontname correctly.

## Acknowledgments
 - [Myaamori-Aegisub-Scripts](https://github.com/TypesettingTools/Myaamori-Aegisub-Scripts)
 - [fontmerge](https://github.com/WheneverDev/fontmerge)
