# FontCollector
[![FontCollector - Version](https://img.shields.io/pypi/v/fontcollector.svg)](https://pypi.org/project/FontCollector)
[![FontCollector - Python Version](https://img.shields.io/pypi/pyversions/fontcollector.svg)](https://pypi.org/project/FontCollector)
[![FontCollector - Downloads](https://img.shields.io/pypi/dm/fontcollector.svg)](https://pypistats.org/packages/fontcollector)
[![FontCollector - Coverage](https://img.shields.io/codecov/c/github/moi15moi/FontCollector)](https://app.codecov.io/github/moi15moi/FontCollector)
[![FontCollector - mypy](https://img.shields.io/badge/mypy-checked-blue)](https://github.com/moi15moi/FontCollector/actions?query=branch:main)

FontCollector for Advanced SubStation Alpha file.
This tool allows to recover and/or mux the fonts necessary in an mkv.
## Installation
```
pip install FontCollector
```
## Dependencies
-  [MKVToolNix](https://mkvtoolnix.download/downloads.html)

## FontCollector Usage
```console
$ fontcollector --help
usage: fontcollector [-h] --input INPUT [INPUT ...] [-mkv MKV] [--output OUTPUT] [-mkvtoolnix MKVTOOLNIX] [--delete-fonts] [--additional-fonts ADDITIONAL_FONTS [ADDITIONAL_FONTS ...]]
                     [--additional-fonts-recursive ADDITIONAL_FONTS_RECURSIVE [ADDITIONAL_FONTS_RECURSIVE ...]] [--exclude-system-fonts] [--collect-draw-fonts] [--dont-convert-variable-to-collection] [--logging [LOGGING]]

FontCollector for Advanced SubStation Alpha file.

options:
  -h, --help            show this help message and exit
  --input INPUT [INPUT ...], -i INPUT [INPUT ...]
                        Subtitles file. Must be an ASS file/directory. You can specify more than one .ass file/path.
  -mkv MKV
                        Video where the fonts will be merge. Must be a Matroska file.
  --output OUTPUT, -o OUTPUT
                        Destination path of the font. If -o and -mkv aren't specified, it will be the current path.
  -mkvtoolnix MKVTOOLNIX
                        Path to the MKVToolNix folder if not in variable environments. If -mkv is not specified, it will do nothing.
  --delete-fonts, -d
                        If -d is specified, it will delete the font attached to the mkv before merging the new needed font. If -mkv is not specified, it will do nothing.
  --additional-fonts ADDITIONAL_FONTS [ADDITIONAL_FONTS ...], -add-fonts ADDITIONAL_FONTS [ADDITIONAL_FONTS ...]
                        May be a directory containing font files or a single font file. You can specify more than one additional-fonts. If it is a directory, it won't search recursively for fonts
  --additional-fonts-recursive ADDITIONAL_FONTS_RECURSIVE [ADDITIONAL_FONTS_RECURSIVE ...], -add-fonts-rec ADDITIONAL_FONTS_RECURSIVE [ADDITIONAL_FONTS_RECURSIVE ...]
                        Path to font directory, which will be recursively searched for fonts.
  --exclude-system-fonts
                        If specified, FontCollector won't use the system font to find the font used by an .ass file.
  --collect-draw-fonts
                        If specified, FontCollector will collect the font used by the draw. For more detail when this is usefull, see: https://github.com/libass/libass/issues/617
  --dont-convert-variable-to-collection
                        If specified, FontCollector won't convert variable font to a font collection. see: https://github.com/libass/libass/issues/386
  --logging [LOGGING], -log [LOGGING]
                        Destination path of log. If it isn't specified, it will be YYYY-MM-DD--HH-MM-SS_font_collector.log.
```
## Examples
Recover fonts from 2 .ass files and save them in the current folder
```
fontCollector -i "file1.ass" "file2.ass"
```
Take all the .ass files from the current folder and save the font in the current folder
```
fontCollector -i .
```
Mux font from .ass file into an mkv
```
fontCollector -i "file1.ass" -mkv "example.mkv" -mkvtoolnix "C:\Program Files\MKVToolNix"
```

Mux the font from the .ass file into an mkv and delete the currently attached fonts.
```
fontCollector -i "file1.ass" -mkv "example.mkv" -mkvtoolnix "C:\Program Files\MKVToolNix" -d
```
## MKVFontValidator Usage
```console
$ mkvfontvalidator --help
usage: mkvfontvalidator [-h] -mkv MKV [-mkvtoolnix MKVTOOLNIX] [--need-draw-fonts] [--delete-fonts-not-used] [--logging [LOGGING]]

MKV font validator for Advanced SubStation Alpha file.

options:
  -h, --help
                        show this help message and exit
  -mkv MKV
                        The video file to be verified. Must be a Matroska file.
  -mkvtoolnix MKVTOOLNIX
                        Path to the MKVToolNix folder if not in variable environments.
  --need-draw-fonts
                        If specified, MKVFontValidator will report a error if a font used in a draw isn't muxed to the mkv. For more detail when this is usefull, see: https://github.com/libass/libass/issues/617
  --delete-fonts-not-used, -d
                        If specified, MKVFontValidator will remove the fonts that aren't used by the subtitle(s) of the mkv file.
  --logging [LOGGING], -log [LOGGING]
                        Destination path of log. If it isn't specified, it will be YYYY-MM-DD--HH-MM-SS_mkvfontvalidator.log.
```
## Variable Font
Since [Libass](https://github.com/libass/libass/issues/386) does not support [variable font](https://docs.microsoft.com/en-us/typography/opentype/spec/otvaroverview), this tool will automatically generate a [OpenType Font Collection](https://docs.microsoft.com/en-us/typography/opentype/spec/otff#font-collections). The generated collection is designed to simulate how [VSFilter](https://en.wikipedia.org/wiki/DirectVobSub)/[GDI](https://en.wikipedia.org/wiki/Graphics_Device_Interface) handles variable font.
## Acknowledgments
 - [fontmerge](https://github.com/WheneverDev/fontmerge) for the idea to automatically merge the font into the mkv.
 - [Myaamori-Aegisub-Scripts](https://github.com/TypesettingTools/Myaamori-Aegisub-Scripts) Without this tool, I probably could never have created the fontCollector. I got a lot of inspiration from his work.
 - [PyonFX](https://github.com/CoffeeStraw/PyonFX) I inspired myself from his setup.py to create mine.
 - [rcombs](https://github.com/rcombs) for her help with how VSFilter pick font when faux-bold need to be applied.
 - [assfc](https://github.com/tp7/assfc) for all the idea behind the font_loader.
 - [Christopher Leung](https://www.linkedin.com/in/christopher-leung-755a291) for his help on how GDI handle variable font.
