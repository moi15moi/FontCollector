import ass
import fixedint
import os
import regex
import shutil
import subprocess
import sys
from argparse import ArgumentParser
from fontTools import ttLib
from matplotlib import font_manager
from pathlib import Path
from struct import error as struct_error
from typing import Dict, List, NamedTuple, Set

from colorama import Fore, init
init(convert=True)

__version__ = "0.6.2"

# GLOBAL VARIABLES
LINE_PATTERN = regex.compile(r"(?:\{(?P<tags>[^}]*)\}?)?(?P<text>[^{]*)")
FIRST_COMMENT = regex.compile(r"^.*?(?<=\\)")

TAG_ITALIC_PATTERN = regex.compile(r"(?<=\\\s*i\s*)[+-]?\d*(?=\s*\)*\s*\\|\s*\)*\s*$)")
TAG_BOLD_PATTERN = regex.compile(r"(?<=\\\s*b\s*)[+-]?\d*(?=\s*\)*\s*\\|\s*\)*\s*$)")
TAG_FN_PATTERN = regex.compile(r"(?<=\\\s*fn).*?(?=\\|(?<=\(.*?\)|\)))")
TAG_R_PATTERN = regex.compile(r"(?<=\\\s*r).*?(?=\\|(?<=\(.*?\)|\)))")


class Font(NamedTuple):
    fontPath: str
    fontName: str
    weight: int
    italic: bool
    weightCompare: fixedint.Int32
    exact_name: str # if the font is a TrueType, it will be the "full_name". if the font is a OpenType, it will be the postscript name

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


def isMkv(fileName:Path) -> bool:
    """
    Parameters:
        fileName (Path): The file name. Example: "example.mkv"
    Returns:
        True if the mkv is an mkv file, false in any others cases

    Thanks to https://github.com/TypesettingTools/Myaamori-Aegisub-Scripts/blob/f2a52ee38eeb60934175722fa9d7f2c2aae015c6/scripts/fontvalidator/fontvalidator.py#L414
    """
    with open(fileName, 'rb') as f:
        return f.read(4) == b'\x1a\x45\xdf\xa3'


def stripFontname(fontName:str) -> str:
    """
    Parameters:
        fontName (str): The font name.
    Returns:
        The font without an @ at the beginning

    Thanks to https://github.com/TypesettingTools/Myaamori-Aegisub-Scripts/blob/f2a52ee38eeb60934175722fa9d7f2c2aae015c6/scripts/fontvalidator/fontvalidator.py#L33
    """
    if fontName.startswith('@'):
        return fontName[1:]
    else:
        return fontName


def parseTags(tags: str, styles: Dict[str, AssStyle], style: AssStyle) -> AssStyle:
    """
    Parameters:
        tags (str): A string containing tag. Ex: "\fnBell MT\r\i1\b1"
        styles (Dict[str, AssStyle]): The key is the style name. It contains all the style in the [V4+ Styles] section of an .ass
        style (AssStyle): The line style of the tags we received
    Returns:
        The new AssStyle according to the tags
    """
    styleName = TAG_R_PATTERN.findall(tags)


    if(len(styleName) > 0 and len(styleName[0]) > 0 and len(styleName[-1]) > 0):
        styleName = styleName[-1]

        # We do not allow "(" or ")" in a fontName. Also it can start with whitespace at the beginning. Ex: "\r Jester" would be invalid
        if("(" not in styleName and ")" not in styleName and styleName.lstrip() == styleName):
            if styleName.rstrip() in styles:
                style = styles[styleName.rstrip()]
        else:
            print(Fore.LIGHTRED_EX + f"Warning: style can not contains \"(\" or \")\" and/or whitespace at the beginning. The style \"{styleName}\" will be ignored." + Fore.RESET)
    
    tagsList = TAG_R_PATTERN.split(tags)
    cleanTag = tagsList[-1]

    if(cleanTag):
        bold = TAG_BOLD_PATTERN.findall(cleanTag)

        if(bold and bold[-1]):
            # We do [-1], because we only want the last match
            boldNumber = int(bold[-1])

            if boldNumber == 0:
                style = style._replace(weight=400)
            elif boldNumber == 1:
                style = style._replace(weight=700)
                
            # if the \bX is less than 0 or [2,100[, it will take the style weight.
            # Everything else will take the X of \bX
            elif not (boldNumber < 0 or 2 <= boldNumber < 100):
                style = style._replace(weight=boldNumber)

        italic = TAG_ITALIC_PATTERN.findall(cleanTag)

        if(italic and italic[-1]):
            # We do [-1], because we only want the last match
            italicNumber = int(italic[-1])
            style = style._replace(italic=bool(italicNumber))

        # Get the last occurence + the first element in the array.
        font = TAG_FN_PATTERN.findall(cleanTag)

        if(len(font) > 0 and len(font[0]) > 0 and len(font[-1]) > 0):
            font = font[-1]

            # We do not allow "(" or ")" in a fontName
            if("(" not in font and ")" not in font):
                style = style._replace(fontName=stripFontname(font.strip().lower()))
            else:
                print(Fore.LIGHTRED_EX + "Warning: fontName can not contains \"(\" or \")\"." + Fore.RESET)

    return style


def parseLine(lineRawText: str, styles: Dict[str, AssStyle], style: AssStyle) -> Set[AssStyle]:
    """
    Parameters:
        lineRawText (str): Ass line. Example: {\fnJester\b1}This is an example!
        styles (Dict[str, AssStyle]): The key is the style name. It contains all the style in the [V4+ Styles] section of an .ass
        style (AssStyle): Style applied to this line
    Returns:
        A set that contains all the possible style in a line.
    """
    allLineTags = ""
    styleSet = set()

    # The last match of the regex is useless, so we remove it
    for tags, text in LINE_PATTERN.findall(lineRawText)[:-1]:
        if text:
            """
            I add \\ at the end of each tags block, because the regex could not work properly.

            Moreover, I remove any "FIRST_COMMENT".
            Example 1:
            {blablabla\b1\fnJester}FontCollectorTest --> Would remove "blablabla". So, we only have "\b1\fnJester\"
            
            Example 2:
            {\b1\fnJester}FontCollectorTest{this is an comment} --> Would remove "this is an comment". So, we only have "\b1\fnJester\\"


            Moreover, I add a \\ at the beginning because the regex remove the first \\
            """
            tags += "\\"
            allLineTags += "\\" + FIRST_COMMENT.sub('',tags)
            print(allLineTags)
            styleSet.add(parseTags(allLineTags, styles, style))

    return styleSet


def getAssStyle(subtitle: ass.Document, fileName:str) -> Set[AssStyle]:
    """
    Parameters:
        subtitle (ass.Document): Ass Document
        fileName (str): The file name of the ass. Ex: "test.ass"
    Returns:
        A set containing all style
    """
    styleSet = set()
    styles = {style.name: AssStyle(stripFontname(style.fontname.strip().lower()), 700 if style.bold else 400, style.italic)
              for style in subtitle.styles}

    for i, line in enumerate(subtitle.events):
        if(isinstance(line, ass.Dialogue)):
            try:
                style = styles[line.style]
                styleSet.update(parseLine(line.text, styles, style))

            except KeyError:
                sys.exit(print(Fore.RED + f"Error: unknown style \"{line.style}\" on line {i+1}. You need to correct the .ass file named \"{fileName}\"" + Fore.RESET))

    return styleSet


def copyFont(fontCollection: Set[Font], outputDirectory: Path):
    """
    Parameters:
        fontCollection (Set[Font]): Font collection
        outputDirectory (Path): The output directory where the font are going to be save
    """
    for font in fontCollection:
        shutil.copy(font.fontPath, outputDirectory)


def searchFont(fontCollection: Set[Font], style: AssStyle, searchByFontName: bool = True) -> List[Font]:
    """
    Parameters:
        fontCollection (Set[Font]): Font collection
        style (AssStyle): An AssStyle
        searchByFontName (bool): If true, it will search the font by it's name. If false, it will search the font by it's exact_name.
    Returns:
        The font that match the best to the AssStyle
    """
    fontMatch = []

    for font in fontCollection:
        if(searchByFontName and font.fontName == style.fontName) or (not searchByFontName and font.exact_name == style.fontName):

            font = font._replace(weightCompare=fixedint.Int32(abs(style.weight - font.weight)))

            if((style.weight - font.weight) > 150):
                font = font._replace(weightCompare=fixedint.Int32(font.weightCompare-120))

            # Thanks to rcombs@github: https://github.com/libass/libass/issues/613#issuecomment-1102994528
            font = font._replace(weightCompare=(((((((font.weightCompare)<<3)+(font.weightCompare))<<3))+(font.weightCompare))>>8))

            fontMatch.append(font)

    # I sort the italic, because I think we prefer a font weight that do not match the weight and is not italic.
    # Also, the last sort parameter (font.weight) is totally optional. In VSFilter, when the weightCompare is the same, it will take the first one, so the order is totally random, so VSFilter will not always display the same font.
    if(style.italic):
        fontMatch.sort(key=lambda font: (-font.italic, font.weightCompare, font.weight))
    else:
        fontMatch.sort(key=lambda font: (font.italic, font.weightCompare, font.weight))

    return fontMatch


def findUsedFont(fontCollection: Set[Font], styleCollection: Set[AssStyle]) -> Set[Font]:
    """
    Parameters:
        fontCollection (Set[Font]): Font collection
        styleCollection (Set[AssStyle]): Style collection
    Returns:
        A set containing all the font that match the styleCollection
    """
    fontsMissing = set()
    fontsFound = set()

    for style in styleCollection:
        fontMatch = searchFont(fontCollection, style)

        if(len(fontMatch) == 0):
            # if we get here, there is two possibility.
            # 1 - We don't have the font
            # 2 - We have the font, but it match with the Font.exact_name
            # That's why we redo a search
            fontMatch = searchFont(fontCollection, style, False)

        if(len(fontMatch) == 0):
            # That was the first possibility
            fontsMissing.add(style.fontName)
        else:
            # That was the second possibility
            fontsFound.add(fontMatch[0])

    if(len(fontsMissing) > 0):
        print(Fore.RED + "\nError: Some fonts were not found. Are they installed? :")
        print("\n".join(fontsMissing))
        print(Fore.RESET, end = "")
    else:
        print(Fore.LIGHTGREEN_EX + "All fonts found" + Fore.RESET)

    return fontsFound


def createFont(fontPath: str) -> Font:
    """
    Parameters:
        fontPath (str): Font path. The font can be a .ttf, .otf or .ttc
    Returns:
        An Font object that represent the file at the fontPath
    """

    font = ttLib.TTFont(fontPath, fontNumber=0)
    details = {}
    found = False
    for record in font['name'].names:
        if record.langID == 0 or record.langID == 1033:
            try:
                details[record.nameID] = record.toUnicode()
                found = True

            except UnicodeDecodeError:
                pass
        elif not found:
            if b'\x00' in record.string:
                try:
                    details[record.nameID] = record.string.decode('utf-16-be')
                except UnicodeDecodeError:
                    pass
    
    # https://docs.microsoft.com/en-us/typography/opentype/spec/name#platform-encoding-and-language-ids
    fontName = details[1].strip().lower()

    # Thanks to Myaa for this: https://github.com/TypesettingTools/Myaamori-Aegisub-Scripts/blob/f2a52ee38eeb60934175722fa9d7f2c2aae015c6/scripts/fontvalidator/fontvalidator.py#L139
    # https://docs.microsoft.com/en-us/typography/opentype/spec/name#name-ids
    # If TrueType, take "full names" which has the id 4
    # If OpenType, ttake "PostScript" which has the id 6
    exact_names = (details[6] if (font.has_key("CFF ") and details[6]) else details[4]).strip().lower()

    try:
        # https://docs.microsoft.com/en-us/typography/opentype/spec/os2#fss
        isItalic = font["OS/2"].fsSelection & 0b1 > 0

        # https://docs.microsoft.com/en-us/typography/opentype/spec/os2#usweightclass
        weight = font['OS/2'].usWeightClass
    except struct_error:
        print(Fore.LIGHTRED_EX + f"Warning: The file \"{fontPath}\" does not have an OS/2 table. This can lead to minor errors. The default style will be applied" + Fore.RESET)
        isItalic = False
        weight = 400

    # Some font designers appear to be under the impression that weights are 1-9 (From: https://github.com/Ristellise/AegisubDC/blob/master/src/font_file_lister_coretext.mm#L70)
    if(weight <= 9):
        weight *= 100

    # The weightCompare is set to 0. It could be any value. It does not care
    return Font(fontPath, fontName, weight, isItalic, fixedint.Int32(0), exact_names)


def initializeFontCollection(additionalFontsPath: List[Path]) -> Set[Font]:
    """
    Search all the installed font and save it in fontCollection
    Parameters:
        additionalFontsPath (List[Path]): List of path that contains font. The list can contains directory and/or file
    Returns:
        List that contains all the font that the system could find including the one in additionalFontsDirectoryPath and additionalFontsFilePath
    """
    fontCollection = set()

    # TODO See if this line is required
    # font_manager._load_fontmanager(try_read_cache=False)

    # Even if I write ttf, it will also search for .otf and .ttc file
    fontsPath = font_manager.findSystemFonts(fontpaths=None, fontext='ttf')

    for fontPath in additionalFontsPath:
        if fontPath.is_dir():
            fontsPath.extend(font_manager.findSystemFonts(fontpaths=str(fontPath), fontext='ttf'))
        elif fontPath.is_file():
            fontsPath.append(str(fontPath))

    for fontPath in fontsPath:
        fontCollection.add(createFont(fontPath))

    return fontCollection


def deleteFonts(mkvFile:Path, mkvpropedit:Path):
    """
    Delete all mkv attached font

    Parameters:
        mkvFile (Path): Path to mkvFile
        mkvpropedit (Path): Path to mkvpropedit
    """
    mkvpropedit_args = [
        '"' + str(mkvFile) + '"'
        ]

    mkvpropedit_args.insert(0, str(mkvpropedit))

    # We only want to remove ttf, ttc or otf file
    # This is from mpv: https://github.com/mpv-player/mpv/blob/305332f8a06e174c5c45c9c4547293502ac7ecdb/sub/sd_ass.c#L101
    mkvpropedit_args.append("--delete-attachment mime-type:application/x-truetype-font")
    mkvpropedit_args.append("--delete-attachment mime-type:application/vnd.ms-opentype")
    mkvpropedit_args.append("--delete-attachment mime-type:application/x-font-ttf")
    mkvpropedit_args.append("--delete-attachment mime-type:application/x-font")
    mkvpropedit_args.append("--delete-attachment mime-type:application/font-sfnt")
    mkvpropedit_args.append("--delete-attachment mime-type:font/collection")
    mkvpropedit_args.append("--delete-attachment mime-type:font/otf")
    mkvpropedit_args.append("--delete-attachment mime-type:font/sfnt")
    mkvpropedit_args.append("--delete-attachment mime-type:font/ttf")

    subprocess.call(" ".join(mkvpropedit_args))
    print(Fore.LIGHTGREEN_EX + "Successfully deleted fonts with mkv" + Fore.RESET)


def mergeFont(fontCollection: Set[Font], mkvFile: Path, mkvpropedit: Path):
    """
    Parameters:
        fontCollection (Path): All font needed to be merge in the mkv
        mkvFile (Path): Mkv file path
        mkvpropedit (Path): Mkvpropedit file path
    """
    mkvpropedit_args = [
        '"' + str(mkvFile) + '"'
        ]

    mkvpropedit_args.insert(0, str(mkvpropedit))


    for font in fontCollection:
        mkvpropedit_args.append("--add-attachment " + '"' + font.fontPath + '"')

    subprocess.call(" ".join(mkvpropedit_args))
    print(Fore.LIGHTGREEN_EX + "Successfully merging fonts with mkv" + Fore.RESET)


def main():
    parser = ArgumentParser(description="FontCollector for Advanced SubStation Alpha file.")
    parser.add_argument('--input', '-i', nargs='+', required=True, metavar="[.ass file]", help="""
    Subtitles file. Must be an ASS file. You can specify more than one .ass file.
    """)
    parser.add_argument('-mkv', metavar="[.mkv input file]", help="""
    Video where the fonts will be merge. Must be a Matroska file.
    """)
    parser.add_argument('--output', '-o', nargs='?', const='', metavar="path", help="""
    Destination path of the font. If not specified, it will be the current path.
    """)
    parser.add_argument('-mkvpropedit', metavar="[path]", help="""
    Path to mkvpropedit.exe if not in variable environments. If -mkv is not specified, it will do nothing.
    """)
    parser.add_argument('--delete-fonts', '-d', action='store_true', help="""
    If -d is specified, it will delete the font attached to the mkv before merging the new needed font. If -mkv is not specified, it will do nothing.
    """)
    parser.add_argument('--additional-fonts', nargs='*', metavar="path", help="""
    May be a directory containing font files or a single font file. You can specify more than one additional-fonts.
    """)

    args = parser.parse_args()

    # Parse args
    assFileList = []
    for input in args.input:
        if(os.path.isfile(input)):
            input = Path(input)

            split_tup = os.path.splitext(input)
            file_extension = split_tup[1]

            if(".ass" != file_extension):
                return print(Fore.RED + "Error: the input file is not an .ass file." + Fore.RESET)
            else:
                assFileList.append(input)
        else:
            return print(Fore.RED + "Error: the input file does not exist" + Fore.RESET)

    output = ""
    if args.output is not None:

        output = Path(args.output)

        if not os.path.isdir(output):
            return print(Fore.RED + "Error: the output path is not a valid folder." + Fore.RESET)

    mkvFile = ""
    if args.mkv is not None:
        mkvFile = Path(args.mkv)

        if not os.path.isfile(mkvFile):
            return print(Fore.RED + "Error: the mkv file specified does not exist." + Fore.RESET)
        elif not isMkv(mkvFile):
            return print(Fore.RED + "Error: the mkv file specified is not an .mkv file." + Fore.RESET)

    mkvpropedit = ""
    if mkvFile:
        if(args.mkvpropedit is not None and os.path.isfile(args.mkvpropedit)):
            mkvpropedit = Path(args.mkvpropedit)
        else:
            mkvpropedit = shutil.which("mkvpropedit")

            if not mkvpropedit:
                return print(Fore.RED + "Error: mkvpropedit in not in your environnements variable, add it or specify the path to mkvpropedit.exe with -mkvpropedit." + Fore.RESET)

        delete_fonts = args.delete_fonts

    additionalFonts = []
    if(args.additional_fonts is not None):
        for additional_font in args.additional_fonts:
            path = Path(additional_font)
            additionalFonts.append(path)

    fontCollection = initializeFontCollection(additionalFonts)

    styleCollection = set()
    for assInput in assFileList:
        with open(assInput, encoding='utf_8_sig') as f:
            subtitles = ass.parse(f)

        styleCollection.update(getAssStyle(subtitles, os.path.basename(assInput)))

    fontsUsed = findUsedFont(fontCollection, styleCollection)

    if output:
        copyFont(fontsUsed, output)

    if mkvFile:
        if delete_fonts:
            deleteFonts(mkvFile, mkvpropedit)

        mergeFont(fontsUsed, mkvFile, mkvpropedit)


if __name__ == "__main__":
    sys.exit(main())