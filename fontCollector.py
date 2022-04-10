import os
import shutil
import sys
import re
import ass
import argparse
from matplotlib import font_manager
from contextlib import redirect_stderr
from typing import NamedTuple
from fontTools import ttLib

from colorama import Fore, init
init(convert=True)

__version__ = "0.1"

# GLOBAL VARIABLES
fontCollection = []
styleCollection = []

LINE_PATTERN = re.compile(r"(?:\{(?P<tags>[^}]*)\}?)?(?P<text>[^{]*)")
INT_PATTERN = re.compile(r"[+-]?\d+")

TAG_R_PATTERN = re.compile(r"\\r")
TAG_ITALIC_PATTERN = re.compile(r"\\i[0-9]*")
TAG_BOLD_PATTERN = re.compile(r"\\b[0-9]*")
TAG_FN_PATTERN = re.compile(
    r"(?<=\\fn)(.*?)(?=\)\\|\\|(?<=\w)(?=$)(?<=\w)(?=$))|(?<=fn)(.*?)(\()(.*?)(\))|(?<=\\fn)(.*?)(?=\\)|(?<=\\fn)(.*?)(?=\)$)|(?<=\\fn)(.*?)(?=\)\\)")


class Font(NamedTuple):
    fontPath: str
    fontName: str
    bold: bool
    italic: bool

    def __eq__(self, other):
        return self.fontName == other.fontName and self.bold == other.bold and self.italic == other.italic

class AssStyle(NamedTuple):
    fontName: str
    bold: bool
    italic: bool

    def __eq__(self, other):
        return self.fontName == other.fontName and self.bold == other.bold and self.italic == other.italic

    def __str__(self):
        return "FontName: " + self.fontName + " Bold: " + str(self.bold) + " Italic: " + str(self.italic)


def parse_tags(tags: str, style: AssStyle) -> AssStyle:
    """
    Parameters:
        tags (str): A str containing tag. Ex: "\fnBell MT\r\i1\b1"
    Returns:
        The current text (text does not means line!) AssStyle
    """

    tagsList = TAG_R_PATTERN.split(tags)

    cleanTag = tagsList[-1]

    if(cleanTag):
        bold = TAG_BOLD_PATTERN.findall(cleanTag)
        if(bold):
            # We do [-1], because we only want the last match
            boldNumber = INT_PATTERN.findall(bold[-1])

            if(boldNumber[0] == "1"):
                style = style._replace(bold=True)

        italic = TAG_ITALIC_PATTERN.findall(cleanTag)
        if(italic):
            # We do [-1], because we only want the last match
            italicNumber = INT_PATTERN.findall(italic[-1])

            if(italicNumber[0] == "1"):
                style = style._replace(italic=True)

        # Get the last occurence + the first element in the array.
        font = TAG_FN_PATTERN.findall(cleanTag)[-1][0]

        # Aegisub does not allow "(" or ")" in a fontName
        if("(" not in font and ")" not in font):
            style = style._replace(fontName=font)
        else:
            print(Fore.RED + "FontName can not contains \"(\" or \")\"." + Fore.WHITE)

    return style


def parse_line(line_raw_text: str, style: AssStyle):
    """
    Parameters:
        line_raw_text (str): Ass line
        style (AssStyle): Style of the line_raw_text
    """
    allLineTags = ""

    # The last match of the regex is useless, so we remove it
    for tags, text in LINE_PATTERN.findall(line_raw_text)[:-1]:

        allLineTags += tags
        styleCollection.append(parse_tags(allLineTags, style))


def getAssStyle(subtitle: ass.Document) -> set:
    """
    Parameters:
        subtitle (ass.Document): Ass Document
    Returns:
        A set containing all unique style
    """

    styles = {style.name: AssStyle(style.fontname, style.bold, style.italic)
              for style in subtitle.styles}

    for i, line in enumerate(subtitle.events):
        nline = i + 1
        if(isinstance(line, ass.Dialogue)):

            try:
                style = styles[line.style]

            except KeyError:
                print(f"Warning: Unknown style {line.style} on line {nline}; assuming default style")
                
                # I write "aqqiwjwj", because we can't get the path of the default without doing that
                style = AssStyle(font_manager.findfont("aqqiwjwj"), False, False)

            parse_line(line.text, style)

    uniqueStyle = set(styleCollection)

    return uniqueStyle


def searchFontByName(fontName: str) -> list:
    """
    Parameters:
        fontName (str): Font name
    Returns:
        A list containing all font that match with the fontName
    """
    fontMatch = []

    for font in fontCollection:
        if(font.fontName.lower() == fontName.lower()):
            fontMatch.append(font)

    return fontMatch


def searchFontBoldAndItalic(fontList:list) -> Font:
    """
    Parameters:
        fontList (list): List that contains font
    Returns:
        Font
    """

    for font in fontList:
        if(font.bold and font.italic):
            return font

    font = searchFontBold(fontList)

    if(font is None):
        return searchFontItalic(fontList)
    else:
        return font


def searchFontBold(fontList:list) -> Font:
    """
    Parameters:
        fontList (list): List that contains font
    Returns:
        Font
    """

    for font in fontList:
        if(font.bold and not font.italic):
            return font


def searchFontItalic(fontList:list) -> Font:
    """
    Parameters:
        fontList (list): List that contains font
    Returns:
        Font
    """

    for font in fontList:
        if(font.italic and not font.bold):
            return font


def searchFontRegular(fontList:list) -> Font:
    """
    Parameters:
        fontList (list): List that contains font
    Returns:
        Font
    """

    for font in fontList:
        if(not font.italic and not font.bold):
            return font


def copyFont(styleList:list, outputDirectory: str):
    """
    Copy font to an directory.

    Parameters:
        styleList (list): It contains all the needed style of an .ASS file
        outputDirectory (str): Directory where to save the font file
    """

    for style in styleList:
        fontMatch = searchFontByName(style.fontName)

        if(len(fontMatch) == 1):
            shutil.copy(fontMatch[0].fontPath, outputDirectory)
        else:
            font = None
            if(style.bold and style.italic):
                font = searchFontBoldAndItalic(fontMatch)
            elif(style.bold):
                font = searchFontBold(fontMatch)
            elif(style.italic):
                font = searchFontItalic(fontMatch)

            if(font is None):
                font = searchFontRegular(fontMatch)

            shutil.copy(font.fontPath, outputDirectory)


def getFontName(font_path: str):
    """
    Get font name
    Parameters:
        font_path (str): Font path. The font can be a .ttf, .otf or .ttc
    Returns:
        The font name, Style

    Thanks to https://gist.github.com/pklaus/dce37521579513c574d0?permalink_comment_id=3507444#gistcomment-3507444
    """

    font = ttLib.TTFont(font_path, fontNumber=0, ignoreDecompileErrors=True)
    with redirect_stderr(None):
        names = font['name'].names

    details = {}
    for x in names:
        if x.langID == 0 or x.langID == 1033:
            try:
                details[x.nameID] = x.toUnicode()
            except UnicodeDecodeError:
                details[x.nameID] = x.string.decode(errors='ignore')

    return details[1], details[2]


def parseStyle(style: str):
    """
    ParseStyle

    Parameters:
        style (str): Style 
            Ex: "Bold Italic", "Bold", "Italic", "Regular", "SOME_FONT_NAME"
    Returns:
        IsBold, IsItalic
    """
    isBold = False
    isItalic = False

    if("bold" in style.lower()):
        isBold = True
    if("italic" in style.lower()):
        isItalic = True

    return isBold, isItalic


def initializeFontCollection():
    """
    This method initialize the font collection.

    It search all the installed font and save it in fontCollection
    """
    # TODO See if this line is required
    # font_manager._load_fontmanager(try_read_cache=False)

    # Even if I write ttf, it will also search for .otf and .ttc file
    fontsPath = font_manager.findSystemFonts(fontpaths=None, fontext='ttf')

    for fontPath in fontsPath:
        fontName, style = getFontName(fontPath)

        bold, italic = parseStyle(style)

        fontCollection.append(Font(fontPath, fontName, bold, italic))


def main():
    parser = argparse.ArgumentParser(description="FontCollector for Advanced SubStation Alpha file.")
    parser.add_argument('--input', '-i', metavar="file", help="""
    Subtitles file. Must be an ASS file.
    """)
    parser.add_argument('--output', '-o', metavar="path", help="""
    Destination path of the font
    """)

    args = parser.parse_args()
    
    if(args.input is not None and os.path.isfile(args.input)):
        split_tup = os.path.splitext(args.input)
        file_extension = split_tup[1]

        if(".ass" != file_extension):
            return print(Fore.RED + "fontCollector.py: error: the input file is not an ASS file." + Fore.WHITE)
    else:
        return print(Fore.RED + "fontCollector.py: error: the input file does not exist." + Fore.WHITE)

    if args.output is not None:
        if not os.path.isdir((os.path.dirname(args.output))):
            return print(Fore.RED + "fontCollector.py: error: output path is not a valid folder." + Fore.WHITE)

    initializeFontCollection()

    with open(args.input, encoding='utf_8_sig') as f:
        subtitles = ass.parse(f)

    uniqueStyle = getAssStyle(subtitles)

    copyFont(uniqueStyle, os.path.dirname(args.output))


if __name__ == "__main__":
    sys.exit(main())