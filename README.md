# FontCollector
FontCollector for Advanced SubStation Alpha file.
This tool allows to recover and/or mux the fonts necessary in an mkv.
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
## Examples
Recover fonts from 2 .ass files and save them in the current folder
```
fontCollector -i "file1.ass" "file2.ass" -o
```

Mux font from .ass file into an mkv
```text
fontCollector -i "file1.ass" -mkv "example.mkv" -mkvpropedit "C:\Program Files\MKVToolNix\mkvpropedit.exe"
```

Mux the font from the .ass file into an mkv and delete the currently attached fonts.
```text
fontCollector -i "file1.ass" -mkv "example.mkv" -mkvpropedit "C:\Program Files\MKVToolNix\mkvpropedit.exe" -d
```
## Color code
|Color|What it means|
|--|--|
|![#E74856](https://via.placeholder.com/15/E74856/000000?text=+)|It is just a Warning. You have nothing to do.|
|![#AE0D1B](https://via.placeholder.com/15/AE0D1B/000000?text=+)|Error. The program will stop. You must do something in order for the task to be completed properly.|
|![#14B30B](https://via.placeholder.com/15/14B30B/000000?text=+)|A task went well|

## Know issues
Currently, FontCollector does not always collect font when the font is Japanese or Chinese. It seems to be a problem from [FontTools](https://github.com/fonttools/fonttools) that do not decode the fontname correctly.

## Acknowledgments
 - [fontmerge](https://github.com/WheneverDev/fontmerge) for the idea to automatically merge the font into the mkv.
 - [Myaamori-Aegisub-Scripts](https://github.com/TypesettingTools/Myaamori-Aegisub-Scripts). Without this tool, I probably could never have created the fontCollector. I got a lot of inspiration from his work.
 - [PyonFX](https://github.com/CoffeeStraw/PyonFX). I inspired myself from his setup.py to create mine.
