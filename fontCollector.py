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
from pathlib import Path

from colorama import Fore, init
init(convert=True)

__version__ = "0.3.2"

# GLOBAL VARIABLES
LINE_PATTERN = re.compile(r"(?:\{(?P<tags>[^}]*)\}?)?(?P<text>[^{]*)")
INT_PATTERN = re.compile(r"[+-]?\d+")

TAG_R_PATTERN = re.compile(r"\\r")
TAG_ITALIC_PATTERN = re.compile(r"\\i[0-9]+|\\i\+[0-9]+|\\i\-[0-9]+")
TAG_BOLD_PATTERN = re.compile(r"\\b[0-9]+|\\b\+[0-9]+|\\b\-[0-9]+")
TAG_FN_PATTERN = re.compile(r"(?<=\\fn)(.*?)(?=\)\\|\\|(?<=\w)(?=$)(?<=\w)(?=$))|(?<=fn)(.*?)(\()(.*?)(\))|(?<=\\fn)(.*?)(?=\\)|(?<=\\fn)(.*?)(?=\)$)|(?<=\\fn)(.*?)(?=\)\\)")


class Font(NamedTuple):
    fontPath: str
    fontName: str
    italic: bool
    weight: int

    def __eq__(self, other):
        return self.fontName == other.fontName and self.italic == other.italic and self.weight == other.weight

    def __hash__(self):
        return hash((self.fontName, self.italic, self.weight))

class AssStyle(NamedTuple):
    """
    AssStyle is an instance that does not only represent "[V4+ Styles]" section of an .ass script.
    It can also represent the style at X line.
    """
    fontName: str
    weight: int # a.k.a bold
    italic: bool

    def __eq__(self, other):
        return self.fontName == other.fontName and self.weight == other.weight and self.italic == other.italic

    def __str__(self):
        return "FontName: " + self.fontName + " Weight: " + str(self.weight) + " Italic: " + str(self.italic)

def strip_fontname(fontName:str):
    """
    Parameters:
        fontName (str): The font name.
    Returns:
        The font without an @ at the beginning
    """
    if fontName.startswith('@'):
        return fontName[1:]
    else:
        return fontName


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
            boldNumber = int(INT_PATTERN.findall(bold[-1])[0])

            # Yes, that's not a good way to do it, but I did not find any other solution.
            if boldNumber <= 0:
                style = style._replace(weight=400)
            elif boldNumber == 1:
                style = style._replace(weight=700)
            elif 2 <= boldNumber <= 150:
                style = style._replace(weight=100)
            elif 151 <= boldNumber <= 250:
                style = style._replace(weight=200)
            elif 251 <= boldNumber <= 350:
                style = style._replace(weight=300)
            elif 351 <= boldNumber <= 450:
                style = style._replace(weight=400)
            elif 451 <= boldNumber <= 550:
                style = style._replace(weight=500)
            elif 551 <= boldNumber <= 650:
                style = style._replace(weight=600)
            elif 651 <= boldNumber <= 750:
                style = style._replace(weight=700)
            elif 751 <= boldNumber <= 850:
                style = style._replace(weight=800)
            elif 851 <= boldNumber:
                style = style._replace(weight=900)

        italic = TAG_ITALIC_PATTERN.findall(cleanTag)
        if(italic):
            # We do [-1], because we only want the last match
            italicNumber = INT_PATTERN.findall(italic[-1])

            if(italicNumber[0] == "1"):
                style = style._replace(italic=True)

        # Get the last occurence + the first element in the array.
        font = TAG_FN_PATTERN.findall(cleanTag)

        if(len(font) > 0 and len(font[-1]) > 0):
            font = font[-1][0]

            # Aegisub does not allow "(" or ")" in a fontName
            if("(" not in font and ")" not in font):
                style = style._replace(fontName=strip_fontname(font.strip().lower()))
            else:
                print(Fore.RED + "FontName can not contains \"(\" or \")\"." + Fore.WHITE)

    return style


def parseLine(lineRawText: str, style: AssStyle) -> set:
    """
    Parameters:
        lineRawText (str): Ass line. Example: {\fnJester\b1}This is an example!
        style (AssStyle): Style applied to this line
    """
    allLineTags = ""
    styleSet = set()

    # The last match of the regex is useless, so we remove it
    for tags, text in LINE_PATTERN.findall(lineRawText)[:-1]:

        """
        I add \\} at each tags block.
        Example if I don't add \\}:
        {\b1\fnJester}FontCollectorTest{this is an commentaire} --> Would give me the fontName Jesterthis is an commentaire
        """
        allLineTags += tags + "\\}"
        styleSet.add(parse_tags(allLineTags, style))
    
    return styleSet


def getAssStyle(subtitle: ass.Document, fileName:str) -> set:
    """
    Parameters:
        subtitle (ass.Document): Ass Document
    Returns:
        A set containing all unique style
    """
    styleSet = set()
    styles = {style.name: AssStyle(strip_fontname(style.fontname.strip().lower()), 700 if style.bold else 400, style.italic)
              for style in subtitle.styles}

    for i, line in enumerate(subtitle.events):
        if(isinstance(line, ass.Dialogue)):
            try:
                style = styles[line.style]
                styleSet.update(parseLine(line.text, style))

            except KeyError:
                sys.exit(print(Fore.RED + f"Error: Unknown style \"{line.style}\" on line {i+1}. You need to correct the .ass file named \"{fileName}\"" + Fore.WHITE))

    return styleSet


def searchFont(fontCollection:set, style: AssStyle) -> list:
    """
    Parameters:
        style (AssStyle): Font name
    Returns:
        A list containing all font that match with the fontName
    """
    fontMatch = []

    for fontI in fontCollection:
        if(fontI.fontName == style.fontName):

            # I am not sure if it work like this in libass.
            if(fontI.weight < style.weight - 150 and style.weight <= 850):
                fontI = fontI._replace(weight=fontI.weight+150)

            fontMatch.append(fontI)

    # The sort is very important !
    if(style.italic):
        fontMatch.sort(key=lambda font: (-font.italic, abs(style.weight - font.weight), font.weight))
    else:
        fontMatch.sort(key=lambda font: (font.italic, abs(style.weight - font.weight), font.weight))

    return fontMatch


def copyFont(fontCollection:set, styleCollection:set, outputDirectory: Path):
    """
    Copy font to an directory.

    Parameters:
        styleList (list): It contains all the needed style of an .ASS file
        outputDirectory (Path): Directory where to save the font file
    """
    fontsMissing = set()


    for style in styleCollection:
        fontMatch = searchFont(fontCollection, style)

        if(len(fontMatch) != 0):
            shutil.copy(fontMatch[0].fontPath, outputDirectory)
        else:
            fontsMissing.add(style.fontName)

    if(len(fontsMissing) > 0):
        print(Fore.RED + "\nSome fonts were not found. Are they installed? :")
        print("\n".join(fontsMissing))
        print(Fore.WHITE + "\n")
    else:
        print(Fore.LIGHTGREEN_EX + "All fonts found" + Fore.WHITE)


def createFont(fontPath: str) -> Font:
    """
    Parameters:
        fontPath (str): Font path. The font can be a .ttf, .otf or .ttc
    Returns:
        An Font object
    """

    font = ttLib.TTFont(fontPath, fontNumber=0, ignoreDecompileErrors=True)
    with redirect_stderr(None):
        names = font['name'].names

    details = {}
    for x in names:
        try:
            details[x.nameID] = x.toStr()
        except UnicodeDecodeError:
            details[x.nameID] = x.string.decode(errors='ignore')

    # https://docs.microsoft.com/en-us/typography/opentype/spec/name#platform-encoding-and-language-ids
    fontName = details[1].strip().lower()
    
    try:
        # https://docs.microsoft.com/en-us/typography/opentype/spec/os2#fss
        isItalic = font["OS/2"].fsSelection & 0b1 > 0

        # https://docs.microsoft.com/en-us/typography/opentype/spec/os2#usweightclass
        weight = font['OS/2'].usWeightClass
    except:
        isItalic = False
        weight = 400
        print(Fore.RED + f"Warning: The file \"{fontPath}\" does not have an OS/2 table. This can lead to minor errors." + Fore.WHITE)

    # Some font designers appear to be under the impression that weights are 1-9 (From: https://github.com/Ristellise/AegisubDC/blob/master/src/font_file_lister_coretext.mm#L70)
    if(weight <= 9):
        weight *= 100

    return Font(fontPath, fontName, isItalic, weight)

def initializeFontCollection() -> set:
    """
    This method initialize the font collection.

    It search all the installed font and save it in fontCollection
    """
    fontCollection = set()

    # TODO See if this line is required
    # font_manager._load_fontmanager(try_read_cache=False)

    # Even if I write ttf, it will also search for .otf and .ttc file
    fontsPath = font_manager.findSystemFonts(fontpaths=None, fontext='ttf')

    for fontPath in fontsPath:
        fontCollection.add(createFont(fontPath))

    return fontCollection


def main():
    parser = argparse.ArgumentParser(description="FontCollector for Advanced SubStation Alpha file.")
    parser.add_argument('input', metavar="<Ass file>", help="""
    Subtitles file. Must be an ASS file.
    """)
    parser.add_argument('--output', '-o', metavar="path", help="""
    Destination path of the font. If not specified, it will be the current path.
    """)

    args = parser.parse_args()


    # Parse args
    if(os.path.isfile(args.input)):
        input = Path(args.input)

        split_tup = os.path.splitext(input)
        file_extension = split_tup[1]

        if(".ass" != file_extension):
            return print(Fore.RED + "Error: the input file is not an .ass file." + Fore.WHITE)
    else:
        return print(Fore.RED + "Error: the input file is not an actual file" + Fore.WHITE)

    if args.output is not None:
        output = Path(args.output)

        if not os.path.isdir(output):
            return print(Fore.RED + "Error: output path is not a valid folder." + Fore.WHITE)
    else:
        output = os.getcwd()

    fontCollection = initializeFontCollection()

    with open(input, encoding='utf_8_sig') as f:
        subtitles = ass.parse(f)

    styleCollection = getAssStyle(subtitles, os.path.basename(input))

    copyFont(fontCollection, styleCollection, output)

if __name__ == "__main__":
    sys.exit(main())