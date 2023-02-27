# FontCollector
FontCollector for Advanced SubStation Alpha file.
This tool allows to recover and/or mux the fonts necessary in an mkv.
## Installation
```
pip install FontCollector
```
## Dependencies
-  [MKVToolNix](https://www.fosshub.com/MKVToolNix.html)

## Usage
```console
$ fontcollector --help
usage: fontcollector [-h] --input [INPUT ...] [-mkv MKV] [--output OUTPUT] [-mkvpropedit MKVPROPEDIT] [--delete-fonts]
                     [--additional-fonts ADDITIONAL_FONTS [ADDITIONAL_FONTS ...]] [--exclude-system-fonts]

FontCollector for Advanced SubStation Alpha file.

options:
  -h, --help            show this help message and exit
  --input [INPUT ...], -i [INPUT ...]
                        Subtitles file. Must be an ASS file/directory. You can specify more than one .ass file/path.
                        If no argument is specified, it will take all the font in the current path.
  -mkv MKV              
                        Video where the fonts will be merge. Must be a Matroska file.
  --output OUTPUT, -o OUTPUT
                        Destination path of the font. If -o and -mkv aren't specified, it will be the current path.
  -mkvpropedit MKVPROPEDIT
                        Path to mkvpropedit.exe if not in variable environments. If -mkv is not specified, it will do
                        nothing.
  --delete-fonts, -d    
                        If -d is specified, it will delete the font attached to the mkv before merging the new needed
                        font. If -mkv is not specified, it will do nothing.
  --additional-fonts ADDITIONAL_FONTS [ADDITIONAL_FONTS ...]
                        May be a directory containing font files or a single font file. You can specify more than one
                        additional-fonts.
  --exclude-system-fonts
                        If specified, FontCollector won't use the system font to find the font used by an .ass file.
```
## Examples
Recover fonts from 2 .ass files and save them in the current folder
```
fontCollector -i "file1.ass" "file2.ass"
```
Take all the .ass files from the current folder and save the font in the current folder
```
fontCollector -i
```
Mux font from .ass file into an mkv
```
fontCollector -i "file1.ass" -mkv "example.mkv" -mkvpropedit "C:\Program Files\MKVToolNix\mkvpropedit.exe"
```

Mux the font from the .ass file into an mkv and delete the currently attached fonts.
```
fontCollector -i "file1.ass" -mkv "example.mkv" -mkvpropedit "C:\Program Files\MKVToolNix\mkvpropedit.exe" -d
```
## Variable Font
Since [Libass](https://github.com/libass/libass/issues/386) does not support [variable font](https://docs.microsoft.com/en-us/typography/opentype/spec/otvaroverview), this tool will automatically generate a [OpenType Font Collection](https://docs.microsoft.com/en-us/typography/opentype/spec/otff#font-collections). The generated collection is designed to simulate how VSFilter handles variable font.
## Acknowledgments
 - [fontmerge](https://github.com/WheneverDev/fontmerge) for the idea to automatically merge the font into the mkv.
 - [Myaamori-Aegisub-Scripts](https://github.com/TypesettingTools/Myaamori-Aegisub-Scripts) Without this tool, I probably could never have created the fontCollector. I got a lot of inspiration from his work.
 - [PyonFX](https://github.com/CoffeeStraw/PyonFX) I inspired myself from his setup.py to create mine.
 - [rcombs](https://github.com/rcombs) for her help with how VSFilter pick font when faux-bold need to be applied.
 - [assfc](https://github.com/tp7/assfc) for all the idea behind the font_loader.