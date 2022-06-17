import ass
import os
import regex
import shutil
import subprocess
import sys
from argparse import ArgumentParser
from fixedint import Int32
from fontTools import ttLib
from fontTools.ttLib.tables._n_a_m_e import NameRecord
from matplotlib import font_manager
from pathlib import Path
from struct import error as struct_error
from typing import Dict, List, NamedTuple, Set, Tuple

from colorama import Fore, init
init(convert=True)

__version__ = "1.1.1"

# GLOBAL VARIABLES
LINE_PATTERN = regex.compile(r"(?:\{(?P<tags>[^}]*)\}?)?(?P<text>[^{]*)")
FIRST_COMMENT = regex.compile(r"^[^\\]*(?=\\|$)")

TAG_ITALIC_PATTERN = regex.compile(r"(?<=\\ *i *)(?! |clip|\S*\\i *(?!clip))\d*")
TAG_BOLD_PATTERN = regex.compile(r"(?<=\\ *b *)(?! |lur|ord|e|\S*\\b *(?!lur|ord|e))\d*")
TAG_FN_PATTERN = regex.compile(r"(?<=\\t\s*\(.*\\\s*fn)(?!.*\\\s*fn)[^\\)]*(?=\))|(?<=\\\s*fn)(?!\)$)(?!.*\\\s*fn)[^\\]*(?=\\|$)")
TAG_R_PATTERN = regex.compile(r"(?<=\\t\s*\(.*\\\s*r)(?!.*\\\s*r)[^\\)]*(?=\))|(?<=\\\s*r)(?!\)$)(?!.*\\\s*r)[^\\]*(?=\\|$)")


class Font(NamedTuple):
    fontPath: str
    familyName: Set[str]
    weight: int
    italic: bool
    weightCompare: Int32
    exactName: Set[str] # if the font is a TrueType, it will be the "full_name". if the font is a OpenType, it will be the "postscript name"

    def __eq__(self, other):
        return self.familyName == other.familyName and self.italic == other.italic and self.weight == other.weight and self.exactName == other.exactName

    def __hash__(self):
        return hash((tuple(self.familyName), self.italic, self.weight))

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


def isMkv(fileName:Path) -> bool:
    """
    Parameters:
        fileName (Path): The file name. Example: "example.mkv"
    Returns:
        True if the mkv is an mkv file, false in any others cases

    Thanks to https://github.com/TypesettingTools/Myaamori-Aegisub-Scripts/blob/f2a52ee38eeb60934175722fa9d7f2c2aae015c6/scripts/fontvalidator/fontvalidator.py#L414
    """
    with open(fileName, 'rb') as f:
        # From https://en.wikipedia.org/wiki/List_of_file_signatures
        return f.read(4) == b'\x1a\x45\xdf\xa3'

####
## Parse Ass
####

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

    if styleName and styleName[0]:
        styleName = styleName[0]

        # We do not allow "(" or ")" in a fontName. Also it can't start with whitespace at the beginning. Ex: "\r Italic" would be invalid
        if "(" not in styleName and ")" not in styleName and styleName.lstrip() == styleName:
            if styleName.rstrip() in styles:
                style = styles[styleName.rstrip()]
            else:
                print(Fore.LIGHTRED_EX + f"Warning: The style \"{styleName}\" will be ignored, because it is not in the [V4+ Styles] section." + Fore.RESET)
        else:
            print(Fore.LIGHTRED_EX + f"Warning: Style can not contains \"(\" or \")\" and/or whitespace at the beginning. The style \"{styleName}\" will be ignored." + Fore.RESET)

    tagsList = TAG_R_PATTERN.split(tags)
    cleanTag = tagsList[-1]

    if cleanTag:
        bold = TAG_BOLD_PATTERN.findall(cleanTag)

        if bold and bold[0]:
            boldNumber = int(bold[0])

            if boldNumber == 0:
                style = style._replace(weight=400)
            elif boldNumber == 1:
                style = style._replace(weight=700)

            # if the \bX is less than 0 or [2,100[, it will take the style weight.
            # Everything else will take the X of \bX
            elif not (boldNumber < 0 or 2 <= boldNumber < 100):
                style = style._replace(weight=boldNumber)

        italic = TAG_ITALIC_PATTERN.findall(cleanTag)

        if italic and italic[0]:
            italicNumber = int(italic[0])
            style = style._replace(italic=bool(italicNumber))

        font = TAG_FN_PATTERN.findall(cleanTag)

        if font and font[0]:
            font = font[0]

            # We do not allow "(" or ")" in a fontName
            if("(" not in font and ")" not in font):
                style = style._replace(fontName=stripFontname(font.strip().lower()))
            else:
                print(Fore.LIGHTRED_EX + "Warning: FontName can not contains \"(\" or \")\"." + Fore.RESET)

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
        """
        I remove any "FIRST_COMMENT".
        Example 1:
        {blablabla\b1\fnJester}FontCollectorTest --> Would remove "blablabla". So, we only have "\b1\fnJester"

        Example 2:
        {\b1\fnJester}FontCollectorTest{this is an comment} --> Would remove "this is an comment". So, we only have "\b1\fnJester"

        Moreover, I add a \\ at the beginning because the regex remove the first \\
        """

        allLineTags += FIRST_COMMENT.sub('', tags)
        if text:
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
        if isinstance(line, ass.Dialogue):
            try:
                style = styles[line.style]
                styleSet.update(parseLine(line.text, styles, style))

            except KeyError:
                sys.exit(print(Fore.RED + f"Error: Unknown style \"{line.style}\" on line {i+1}. You need to correct the .ass file named \"{fileName}\"." + Fore.RESET))

    return styleSet

####
## End Parse Ass
####

####
## Font
####

def copyFont(fontCollection: Set[Font], outputDirectory: Path):
    """
    Parameters:
        fontCollection (Set[Font]): Font collection
        outputDirectory (Path): The directory where the font are going to be save
    """
    for font in fontCollection:
        shutil.copy(font.fontPath, outputDirectory)


def searchFont(fontCollection: Set[Font], style: AssStyle, searchByFamilyName: bool = True) -> List[Font]:
    """
    Parameters:
        fontCollection (Set[Font]): Font collection
        style (AssStyle): An AssStyle
        searchByFontName (bool): If true, it will search the font by it's name (which is the family name). If false, it will search the font by it's exactName.
    Returns:
        Ordered list of the font that match the best to the AssStyle
    """
    fontMatch = []

    for font in fontCollection:
        if (searchByFamilyName and style.fontName in font.familyName) or (not searchByFamilyName and style.fontName in font.exactName):

            #if (searchByFamilyName and font.familyName == style.fontName) or (not searchByFamilyName and font.exactName == style.fontName):

            font = font._replace(weightCompare=Int32(abs(style.weight - font.weight)))

            if (style.weight - font.weight) > 150:
                font = font._replace(weightCompare=Int32(font.weightCompare-120))

            # Thanks to rcombs@github: https://github.com/libass/libass/issues/613#issuecomment-1102994528
            font = font._replace(weightCompare=(((((((font.weightCompare)<<3)+(font.weightCompare))<<3))+(font.weightCompare))>>8))

            fontMatch.append(font)

    # The last sort parameter (font.weight) is totally optional. In VSFilter, when the weightCompare is the same, it will take the first one, so the order is totally random, so VSFilter will not always display the same font.
    if style.italic:
        fontMatch.sort(key=lambda font: (font.weightCompare, -font.italic, font.weight))
    else:
        fontMatch.sort(key=lambda font: (font.weightCompare, font.italic, font.weight))

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

        if len(fontMatch) == 0:
            # if we get here, there is two possibility.
            # 1 - We don't have the font
            # 2 - We have the font, but it match with the Font.exactName
            # That's why we redo a search
            fontMatch = searchFont(fontCollection, style, False)

        if len(fontMatch) == 0:
            # That was the first possibility
            fontsMissing.add(style.fontName)
        else:
            # That was the second possibility.
            fontsFound.add(fontMatch[0])

    if len(fontsMissing) > 0:
        print(Fore.RED + "Error: Some fonts were not found. Are they installed? :")
        print("\n".join(fontsMissing))
        print(Fore.RESET, end = "")
    else:
        print(Fore.LIGHTGREEN_EX + "All fonts found" + Fore.RESET)

    return fontsFound



def getPostscriptName(names: List[NameRecord]) -> str:
    """
    Parameters:
        names (List[NameRecord]): Naming table
    Returns:
        The postscript name. It work exactly like FT_Get_Postscript_Name from Freetype
    """

    # Libass use FT_Get_Postscript_Name to get the postscript name: https://github.com/libass/libass/blob/a2b39cde4ecb74d5e6fccab4a5f7d8ad52b2b1a4/libass/ass_fontselect.c#L326
    # FT_Get_Postscript_Name called this method : https://github.com/freetype/freetype/blob/c26f0d0d7e1b24863193ab2808f67798456dfc9c/src/sfnt/sfdriver.c#L1045-L1087
    # Since libass does not support Opentype variation name, we don't need to reproduce this part of the method: https://github.com/freetype/freetype/blob/c26f0d0d7e1b24863193ab2808f67798456dfc9c/src/sfnt/sfdriver.c#L1054-L1062

    def IS_WIN(name):
        # From: https://github.com/freetype/freetype/blob/c26f0d0d7e1b24863193ab2808f67798456dfc9c/src/sfnt/sfdriver.c#L485-L486
        return name.platformID == 3 and (name.platEncID == 1 or name.platEncID == 0)

    def IS_APPLE(name):
        # From: https://github.com/freetype/freetype/blob/c26f0d0d7e1b24863193ab2808f67798456dfc9c/src/sfnt/sfdriver.c#L488-L489
        return name.platformID == 1 and name.platEncID == 0

    win = apple = None

    for name in names:
        nameStr = ""
        try:
            nameStr = name.toUnicode().strip().lower()
        except UnicodeDecodeError:
            continue

        if name.nameID == 6 and len(nameStr) > 0:
            if IS_WIN(name) and (name.langID == 0x409 or not win):
                win = nameStr
            elif IS_APPLE(name) and (name.langID == 0 or not apple):
                apple = nameStr

    if win:
        return win.strip().lower()
    elif apple:
        return apple.strip().lower()
    else:
        return None

def getFontFamilyNameFullName(names: List[NameRecord]) -> Tuple[Set[str], Set[str]]:
    """
    Parameters:
        names (List[NameRecord]): Naming table
    Returns:
        All families and fullnames that are from microsoft
    """

    # https://github.com/libass/libass/blob/a2b39cde4ecb74d5e6fccab4a5f7d8ad52b2b1a4/libass/ass_fontselect.c#L258-L344
    MAX = 100
    families = fullnames = set()

    for name in names:

        if name.platformID == 3 and (name.nameID == 1 or name.nameID == 4):

            try:
                nameStr = name.toUnicode().strip().lower()
            except UnicodeDecodeError:
                continue

            if name.nameID == 1 and len(families) < MAX:
                families.add(nameStr)
            elif name.nameID == 4 and len(fullnames) < MAX:
                fullnames.add(nameStr)

    return families, fullnames

def getFontFamilyNameLikeFontConfig(names: List[NameRecord]) -> str:
    """
    Parameters:
        names (List[NameRecord]): Naming table
    Returns:
        The family name that FontConfig would return in https://gitlab.freedesktop.org/fontconfig/fontconfig/-/blob/d863f6778915f7dd224c98c814247ec292904e30/src/fcfreetype.c#L1492-1505
    """

    # From	https://gitlab.freedesktop.org/fontconfig/fontconfig/-/blob/d863f6778915f7dd224c98c814247ec292904e30/src/fcfreetype.c#L1078
    #		https://github.com/freetype/freetype/blob/b98dd169a1823485e35b3007ce707a6712dcd525/include/freetype/ttnameid.h#L86-L91
    PLATFORM_ID_APPLE_UNICODE = 0
    PLATFORM_ID_MACINTOSH = 1
    PLATFORM_ID_ISO = 2
    PLATFORM_ID_MICROSOFT = 3
    PLATFORM_ID_ORDER = [
        PLATFORM_ID_MICROSOFT,
        PLATFORM_ID_APPLE_UNICODE,
        PLATFORM_ID_MACINTOSH,
        PLATFORM_ID_ISO,
    ]

    def isEnglish(name: NameRecord) -> bool:
        # From https://gitlab.freedesktop.org/fontconfig/fontconfig/-/blob/d863f6778915f7dd224c98c814247ec292904e30/src/fcfreetype.c#L1111-1125
        return (name.platformID, name.langID) in ((1, 0), (3, 0x409))

    def getDebugName(nameID: int, names: List[NameRecord]) -> str:
        # Merge of  - sort logic: https://gitlab.freedesktop.org/fontconfig/fontconfig/-/blob/d863f6778915f7dd224c98c814247ec292904e30/src/fcfreetype.c#L1443
        #           - Iteration logic: https://gitlab.freedesktop.org/fontconfig/fontconfig/-/blob/d863f6778915f7dd224c98c814247ec292904e30/src/fcfreetype.c#L1448-1604
        names = sorted(names, key=lambda name: (PLATFORM_ID_ORDER.index(name.platformID), name.nameID, name.platEncID, -isEnglish(name), name.langID))

        for name in names:
            if name.nameID != nameID:
                continue
            try:
                unistr = name.toUnicode()
            except UnicodeDecodeError:
                continue

            return unistr

    return getDebugName(1, names).strip().lower()


def createFont(fontPath: str) -> List[Font]:
    """
    Parameters:
        fontPath (str): Font path. The font can be a .ttf, .otf or .ttc
    Returns:
        An Font object that represent the file at the fontPath
    """
    fontsTtLib = []
    fonts = []

    with open(fontPath, 'rb') as fontFile:
        fontType = fontFile.read(4)

    if fontType ==  b'ttcf':
        fontsTtLib.extend(ttLib.TTCollection(fontPath).fonts)
    else:
        fontsTtLib.append(ttLib.TTFont(fontPath))

    # Read font attributes
    for fontTtLib in fontsTtLib:
        isTrueType = False
        # From https://github.com/fonttools/fonttools/discussions/2619
        if "glyf" in fontTtLib:
            isTrueType = True

        families, fullnames = getFontFamilyNameFullName(fontTtLib['name'].names)
        if len(families) == 0:
            # This is something like that: https://github.com/libass/libass/blob/a2b39cde4ecb74d5e6fccab4a5f7d8ad52b2b1a4/libass/ass_fontselect.c#L303-L311
            # I arbitrarily decided to use logic from fontconfig, but it could also have been GDI, CoreText, Freetype, etc.
            families.add(getFontFamilyNameLikeFontConfig(fontTtLib['name'].names))

        exactNames = set()

        # https://docs.microsoft.com/en-us/typography/opentype/spec/name#name-ids
        # If TrueType, take "full names" which has the id 4
        # If OpenType, take "PostScript" which has the id 6
        if isTrueType:
            exactNames = fullnames
        else:
            # If not TrueType, it is OpenType
            postscriptName = getPostscriptName(fontTtLib['name'].names)
            if postscriptName:
                exactNames.add(postscriptName)

        try:
            # https://docs.microsoft.com/en-us/typography/opentype/spec/os2#fss
            isItalic = bool(fontTtLib["OS/2"].fsSelection & 1)

            # https://docs.microsoft.com/en-us/typography/opentype/spec/os2#usweightclass
            weight = fontTtLib['OS/2'].usWeightClass
        except struct_error:
            print(Fore.LIGHTRED_EX + f"Warning: The file \"{fontPath}\" does not have an valid OS/2 table. This can lead to minor errors. The default style will be applied." + Fore.RESET)
            isItalic = False
            weight = 400

        # Some font designers appear to be under the impression that weights are 1-9 (From: https://github.com/Ristellise/AegisubDC/blob/master/src/font_file_lister_coretext.mm#L70)
        if weight <= 9:
            weight *= 100

        # The weightCompare is set to 0. It could be any value. It does not care
        fonts.append(Font(fontPath, families, weight, isItalic, Int32(0), exactNames))

    return fonts


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
    font_manager._load_fontmanager(try_read_cache=False)

    # It will return all TrueType and OpenType file
    fontsPath = font_manager.findSystemFonts()

    for fontPath in additionalFontsPath:
        if fontPath.is_dir():
            fontsPath.extend(font_manager.findSystemFonts(fontpaths=str(fontPath)))
        elif fontPath.is_file():
            fontsPath.append(str(fontPath))

    for fontPath in fontsPath:
        fontCollection.update(createFont(fontPath))

    return fontCollection

####
## End Font
####

####
## mkvpropedit task
####

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

####
## End mkvpropedit task
####

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
        if os.path.isfile(input):
            input = Path(input)

            split_tup = os.path.splitext(input)
            file_extension = split_tup[1]

            if ".ass" != file_extension:
                return print(Fore.RED + "Error: The input file is not an .ass file." + Fore.RESET)
            else:
                assFileList.append(input)
        else:
            return print(Fore.RED + "Error: The input file does not exist." + Fore.RESET)

    outputDirectory = ""
    if args.output is not None:

        outputDirectory = Path(args.output)

        if not os.path.isdir(outputDirectory):
            return print(Fore.RED + "Error: The output path is not a valid folder." + Fore.RESET)

    mkvFile = ""
    if args.mkv is not None:
        mkvFile = Path(args.mkv)

        if not os.path.isfile(mkvFile):
            return print(Fore.RED + "Error: The mkv file specified does not exist." + Fore.RESET)
        elif not isMkv(mkvFile):
            return print(Fore.RED + "Error: The mkv file specified is not an .mkv file." + Fore.RESET)

    mkvpropedit = ""
    if mkvFile:
        if args.mkvpropedit is not None and os.path.isfile(args.mkvpropedit):
            mkvpropedit = Path(args.mkvpropedit)
        else:
            mkvpropedit = shutil.which("mkvpropedit")

            if not mkvpropedit:
                return print(Fore.RED + "Error: Mkvpropedit in not in your environnements variable, add it or specify the path to mkvpropedit.exe with -mkvpropedit." + Fore.RESET)

        delete_fonts = args.delete_fonts

    additionalFonts = []
    if args.additional_fonts is not None:
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

    if outputDirectory:
        copyFont(fontsUsed, outputDirectory)

    if mkvFile:
        if delete_fonts:
            deleteFonts(mkvFile, mkvpropedit)

        mergeFont(fontsUsed, mkvFile, mkvpropedit)


if __name__ == "__main__":
    sys.exit(main())