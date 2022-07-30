# FontCollector
FontCollector for Advanced SubStation Alpha file.
This tool allows to recover and/or mux the fonts necessary in an mkv.
## Installation and Update
```
pip install git+https://github.com/moi15moi/FontCollector.git
```
## Dependencies
-  [Python 3.7 or more](https://www.python.org/downloads/)
-  [MKVToolNix](https://www.fosshub.com/MKVToolNix.html)

## Usage
```console
$ fontCollector --help
usage: fontCollector [-h] --input [[.ass file and/or path] ...] [-mkv [.mkv input file]] [--output [path]] [-mkvpropedit [path]] [--delete-fonts] [--additional-fonts [path ...]]

FontCollector for Advanced SubStation Alpha file.

options:
  -h, --help
                        show this help message and exit
  --input [[.ass file and/or path] ...], -i [[.ass file and/or path] ...]
                        Subtitles file. Must be an ASS file/directory. You can specify more than one .ass file/path. If no argument is specified, it will take all the font in the current path.
  -mkv [.mkv input file]
                        Video where the fonts will be merge. Must be a Matroska file.
  --output [path], -o [path]
                        Destination path of the font. If no argument is specified, it will be the current path.
  -mkvpropedit [path]
                        Path to mkvpropedit.exe if not in variable environments. If -mkv is not specified, it will do nothing.
  --delete-fonts, -d
                        If -d is specified, it will delete the font attached to the mkv before merging the new needed font. If -mkv is not specified, it will do nothing.
  --additional-fonts [path ...]
                        May be a directory containing font files or a single font file. You can specify more than one additional-fonts.
```
## Examples
Recover fonts from 2 .ass files and save them in the current folder
```
fontCollector -i "file1.ass" "file2.ass" -o
```
Take all the .ass files from the current folder and save the font in the current folder
```
fontCollector -i  -o
```
Mux font from .ass file into an mkv
```
fontCollector -i "file1.ass" -mkv "example.mkv" -mkvpropedit "C:\Program Files\MKVToolNix\mkvpropedit.exe"
```

Mux the font from the .ass file into an mkv and delete the currently attached fonts.
```
fontCollector -i "file1.ass" -mkv "example.mkv" -mkvpropedit "C:\Program Files\MKVToolNix\mkvpropedit.exe" -d
```
## Color code
|Color|What it means|
|:--:|--|
|![Light yellow - #f9f1a5](https://via.placeholder.com/15/f9f1a5/f9f1a5.png)|It is just a Warning. You have nothing to do.|
|![Red - #c50f1f](https://via.placeholder.com/15/c50f1f/c50f1f.png)|Error. You must do something to get the task accomplished properly.|
|![Light green - #16c60c](https://via.placeholder.com/15/16c60c/16c60c.png)|A task went well|
## Variable Font
Since [Libass](https://github.com/libass/libass/issues/386) does not support [variable font](https://docs.microsoft.com/en-us/typography/opentype/spec/otvaroverview), this tool will automatically generate a [OpenType Font Collection](https://docs.microsoft.com/en-us/typography/opentype/spec/otff#font-collections). The generated collection is designed to simulate how VSFilter handles variable font.
## Acknowledgments
 - [fontmerge](https://github.com/WheneverDev/fontmerge) for the idea to automatically merge the font into the mkv.
 - [Myaamori-Aegisub-Scripts](https://github.com/TypesettingTools/Myaamori-Aegisub-Scripts) Without this tool, I probably could never have created the fontCollector. I got a lot of inspiration from his work.
 - [PyonFX](https://github.com/CoffeeStraw/PyonFX) I inspired myself from his setup.py to create mine.
 - [rcombs](https://github.com/rcombs) for her help with how VSFilter pick font when faux-bold need to be applied.
