import ass
import copy
import freetype
import os
import regex
import shutil
import subprocess
import sys
from argparse import ArgumentParser
from fixedint import Int32
from fontTools import ttLib
from fontTools.ttLib.tables._n_a_m_e import NameRecord
from fontTools.varLib import instancer
from matplotlib import font_manager
from pathlib import Path
from struct import error as struct_error
from typing import Dict, List, Set, Tuple

from colorama import Fore, init
init(convert=True)

__version__ = "1.3.2"

# GLOBAL VARIABLES
LINE_PATTERN = regex.compile(r"(?:\{(?P<tags>[^}]*)\}?)?(?P<text>[^{]*)")
FIRST_COMMENT = regex.compile(r"^[^\\]*(?=\\|$)")

TAG_ITALIC_PATTERN = regex.compile(r"(?<=\\ *i *)(?! |clip|\S*\\i *(?!clip))\d*")
TAG_BOLD_PATTERN = regex.compile(r"(?<=\\ *b *)(?! |lur|ord|e|\S*\\b *(?!lur|ord|e))\d*")
TAG_FN_PATTERN = regex.compile(r"(?<=\\t\s*\(.*\\\s*fn)(?!.*\\\s*fn)[^\\)]*(?=\))|(?<=\\\s*fn)(?!\)$)(?!.*\\\s*fn)[^\\]*(?=\\|$)")
TAG_R_PATTERN = regex.compile(r"(?<=\\t\s*\(.*\\\s*r)(?!.*\\\s*r)[^\\)]*(?=\))|(?<=\\\s*r)(?!\)$)(?!.*\\\s*r)[^\\]*(?=\\|$)")


class Font:
    fontPath: str
    __familyName: Set[str]
    weight: int
    italic: bool
    weightCompare: Int32
    __exactName: Set[str] # if the font is a TrueType, it will be the "full_name". if the font is a OpenType, it will be the "postscript name"
    font: ttLib.ttFont.TTFont

    def __init__(
            self,
            fontPath: str,
            familyNames: Set[str],
            weight: int,
            italic: bool,
            weightCompare: Int32,
            exactNames: Set[str],
            font: ttLib.ttFont.TTFont
        ):
        self.fontPath = fontPath
        self.familyName = familyNames
        self.weight = weight
        self.italic = italic
        self.weightCompare = weightCompare
        self.exactName = exactNames
        self.font = font

    @property
    def familyName(self):
        return self.__familyName

    @familyName.setter
    def familyName(self, value):
        self.__familyName = set([familyName.strip().lower() for familyName in value])

    @property
    def exactName(self):
        return self.__exactName

    @exactName.setter
    def exactName(self, value):
        self.__exactName = set([exactName.strip().lower() for exactName in value])

    def __eq__(self, other):
        return self.familyName == other.familyName and self.italic == other.italic and self.weight == other.weight and self.exactName == other.exactName

    def __hash__(self):
        return hash((tuple(self.familyName), self.italic, self.weight))

    def __repr__(self):
        return "path: %s, familyName: %s, exactName %s\n" % (self.fontPath, self.familyName, self.exactName)

class AssStyle:
    """
    AssStyle is an instance that does not only represent "[V4+ Styles]" section of an .ass script.
    It can also represent the style at X line.
    """
    __fontName: str
    weight: int # a.k.a bold
    italic: bool

    def __init__(
            self,
            fontName: str,
            weight: int,
            italic: bool,
        ):
        self.fontName = fontName
        self.weight = weight
        self.italic = italic

    @property
    def fontName(self):
        return self.__fontName

    @fontName.setter
    def fontName(self, value):
        self.__fontName = stripFontname(value.strip().lower())

    def __eq__(self, other):
        return self.fontName == other.fontName and self.weight == other.weight and self.italic == other.italic

    def __hash__(self):
        return hash((self.fontName, self.weight, self.italic))
    
    def __repr__(self):
        return "fontName: %s, weight: %s, italic %s\n" % (self.fontName, self.weight, self.italic)


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
                style.weight = 400
            elif boldNumber == 1:
                style.weight = 700

            # if the \bX is less than 0 or [2,100[, it will take the style weight.
            # Everything else will take the X of \bX
            elif not (boldNumber < 0 or 2 <= boldNumber < 100):
                style.weight = boldNumber

        italic = TAG_ITALIC_PATTERN.findall(cleanTag)

        if italic and italic[0]:
            italicNumber = int(italic[0])
            style.italic = bool(italicNumber)

        font = TAG_FN_PATTERN.findall(cleanTag)

        if font and font[0]:
            font = font[0]

            # We do not allow "(" or ")" in a fontName
            if("(" not in font and ")" not in font):
                style.fontName = font
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
            styleSet.add(parseTags(allLineTags, styles, copy.copy(style)))

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
    styles = {style.name: AssStyle(style.fontname, 700 if style.bold else 400, style.italic)
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
        # Don't overwrite fonts
        if not os.path.exists(os.path.join(outputDirectory, Path(font.fontPath).name)):
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
    fontsMatch = []

    for font in fontCollection:
        if (searchByFamilyName and style.fontName in font.familyName) or (not searchByFamilyName and style.fontName in font.exactName):

            font.weightCompare = Int32(abs(style.weight - font.weight))

            if (style.weight - font.weight) > 150:
                font.weightCompare = Int32(font.weightCompare-120)

            # Thanks to rcombs@github: https://github.com/libass/libass/issues/613#issuecomment-1102994528
            font.weightCompare = (((((((font.weightCompare)<<3)+(font.weightCompare))<<3))+(font.weightCompare))>>8)

            fontsMatch.append(font)

    # The last sort parameter (font.weight) is totally optional. In VSFilter, when the weightCompare is the same, it will take the first one, so the order is totally random, so VSFilter will not always display the same font.
    if style.italic:
        fontsMatch.sort(key=lambda font: (font.weightCompare, -font.italic, font.weight, 1 if "fvar" in font.font else 0))
    else:
        fontsMatch.sort(key=lambda font: (font.weightCompare, font.italic, font.weight, 1 if "fvar" in font.font else 0))
    return fontsMatch


def findUsedFont(fontCollection: Set[Font], styleCollection: Set[AssStyle], outputDirectory: Path = None) -> Set[Font]:
    """
    Parameters:
        fontCollection (Set[Font]): Font collection
        styleCollection (Set[AssStyle]): Style collection
    Returns:
        A set containing all the font that match the styleCollection
    """
    fontsMissing = set()
    fontsFound = set()

    print(styleCollection)

    for style in styleCollection:
        fontsMatch = searchFont(fontCollection, style)

        if len(fontsMatch) == 0:
            # if we get here, there is two possibility.
            # 1 - We don't have the font
            # 2 - We have the font, but it match with the Font.exactName
            # That's why we redo a search
            fontsMatch = searchFont(fontCollection, style, False)

        if len(fontsMatch) == 0:
            # That was the first possibility
            fontsMissing.add(style.fontName)
        else:
            # That was the second possibility.
            firstFontMatch = fontsMatch[0]

            if "fvar" in firstFontMatch.font:
                firstFontMatch.fontPath = generateFontFromVariableFont(firstFontMatch.font, style.fontName, outputDirectory)

            fontsFound.add(firstFontMatch)


    if len(fontsMissing) > 0:
        print(Fore.RED + "Error: Some fonts were not found. Are they installed? :")
        print("\n".join(fontsMissing))
        print(Fore.RESET, end = "")
    else:
        print(Fore.LIGHTGREEN_EX + "All fonts found" + Fore.RESET)

    return fontsFound


def generateFontFromVariableFont(font: ttLib.ttFont.TTFont, fontName: str, outputDirectory: str) -> str:
    """
    See https://github.com/fonttools/fonttools/discussions/2707 for more detail
    Parameters:
        font (ttLib.ttFont.TTFont): The variable font to be "split"
        fontName (str): The new fontname for the nameIDs [1, 2, 3, 4, 16]
        outputDirectory (str): Path where to save the generated font
    Returns:
        Path where the generated font has been saved
    """
    defaultCoordinates = {}
    for axis in font["fvar"].axes:
        defaultCoordinates[axis.axisTag] = axis.defaultValue

    for instance in font["fvar"].instances:
        if defaultCoordinates == instance.coordinates:
            fontStyle = font["name"].getDebugName(instance.subfamilyNameID)

    # GDI will always return the variable font with the default coordinates
    newFont = instancer.instantiateVariableFont(font, defaultCoordinates)

    for name in sortNamingTable(font["name"].names):
        if name.nameID == 1:
            familyNameRecord = name
            break

    for name in newFont['name'].names:
        # List of nameID to be remove
        if name.nameID in [1, 2, 3, 4, 6, 16, 17, 21, 22, 25]:
            newFont['name'].removeNames(name.nameID, name.platformID, name.platEncID, name.langID)

    newFont['name'].setName(fontName, 1, familyNameRecord.platformID, familyNameRecord.platEncID, familyNameRecord.langID)
    newFont['name'].setName(fontStyle, 2, 3, 1, 0x409)
    newFont['name'].setName(fontName + " " + fontStyle, 3, familyNameRecord.platformID, familyNameRecord.platEncID, familyNameRecord.langID)
    newFont['name'].setName(fontName, 4, familyNameRecord.platformID, familyNameRecord.platEncID, familyNameRecord.langID)
    newFont['name'].setName(fontName, 16, familyNameRecord.platformID, familyNameRecord.platEncID, familyNameRecord.langID)

    savePath = fontName + ".ttf"
    if outputDirectory is not None:
        savePath = os.path.join(outputDirectory, savePath)

    newFont.save(savePath)

    print(Fore.LIGHTRED_EX + f"The font \"{fontName}\" is a Variable Font. Libass doesn't support these kinds of fonts.\n" +
        Fore.LIGHTGREEN_EX + f"\tFontCollector created a valid font at \"{savePath}\".\n" +
        "\tIf you specified -mkv, the font will be muxed into the mkv and save in your current path.\n" +
        "\tIf you specified -o, it will be saved in that path." + Fore.RESET)

    return savePath


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
                # Since we use the windows platform, we can simply use utf_16_be to decode the string: https://docs.microsoft.com/en-us/typography/opentype/spec/name#platform-specific-encoding-and-language-ids-windows-platform-platform-id-3
                # Even libass always use utf_16_be: https://github.com/libass/libass/blob/a2b39cde4ecb74d5e6fccab4a5f7d8ad52b2b1a4/libass/ass_fontselect.c#L283
                # Warning if libass use a day name from other platform, we will need to use name.toUnicode()
                nameStr = name.string.decode('utf_16_be')
            except UnicodeDecodeError:
                continue

            if name.nameID == 1 and len(families) < MAX:
                families.add(nameStr)
            elif name.nameID == 4 and len(fullnames) < MAX:
                fullnames.add(nameStr)

    return families, fullnames


def sortNamingTable(names: List[NameRecord]) -> List[NameRecord]:
    """
    Parameters:
        names (List[NameRecord]): Naming table
    Returns:
        The sorted naming table
    """

    def isEnglish(name: NameRecord) -> bool:
        # From https://gitlab.freedesktop.org/fontconfig/fontconfig/-/blob/d863f6778915f7dd224c98c814247ec292904e30/src/fcfreetype.c#L1111-1125
        return (name.platformID, name.langID) in ((1, 0), (3, 0x409))

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

    return sorted(names, key=lambda name: (PLATFORM_ID_ORDER.index(name.platformID), name.nameID, name.platEncID, -isEnglish(name), name.langID))

def getNameLikeFontConfig(nameID: int, names: List[NameRecord]) -> str:
    """
    Parameters:
        names (List[NameRecord]): Naming table
    Returns:
        The family name that FontConfig would return in https://gitlab.freedesktop.org/fontconfig/fontconfig/-/blob/d863f6778915f7dd224c98c814247ec292904e30/src/fcfreetype.c#L1492-1505
    """

    # Merge of  - sort logic: https://gitlab.freedesktop.org/fontconfig/fontconfig/-/blob/d863f6778915f7dd224c98c814247ec292904e30/src/fcfreetype.c#L1443
    #           - Iteration logic: https://gitlab.freedesktop.org/fontconfig/fontconfig/-/blob/d863f6778915f7dd224c98c814247ec292904e30/src/fcfreetype.c#L1448-1604
    names = sortNamingTable(names)

    for name in names:
        if name.nameID != nameID:
            continue
        try:
            unistr = name.toUnicode()
        except UnicodeDecodeError:
            continue

        return unistr


def getFontAttributesWithFreetype(fontPath: str, fontIndex: int) -> Tuple[bool, int]:
    """
    Parameters:
        fontPath (str): Font path.
    Returns:
        isItalic, weight
    """
    font = freetype.Face(Path(fontPath).open("rb"), fontIndex)
    # From: https://github.com/libass/libass/blob/a2b39cde4ecb74d5e6fccab4a5f7d8ad52b2b1a4/libass/ass_fontselect.c#L318
    isItalic = bool(font.style_flags & freetype.ft_enums.ft_style_flags.FT_STYLE_FLAG_ITALIC)
    # From: https://github.com/libass/libass/blob/a2b39cde4ecb74d5e6fccab4a5f7d8ad52b2b1a4/libass/ass_font.c#L523
    weight = 700 if bool(font.style_flags & freetype.ft_enums.ft_style_flags.FT_STYLE_FLAG_BOLD) else 400

    return isItalic, weight


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
    for fontIndex, fontTtLib in enumerate(fontsTtLib):
        isTrueType = False
        # From https://github.com/fonttools/fonttools/discussions/2619
        if "glyf" in fontTtLib:
            isTrueType = True

        families, fullnames = getFontFamilyNameFullName(fontTtLib['name'].names)
        if len(families) == 0:
            # This is something like that: https://github.com/libass/libass/blob/a2b39cde4ecb74d5e6fccab4a5f7d8ad52b2b1a4/libass/ass_fontselect.c#L303-L311
            # I arbitrarily decided to use logic from fontconfig, but it could also have been GDI, CoreText, etc. It is impossible to know what libass will do.
            familyName = getNameLikeFontConfig(1, fontTtLib['name'].names)

            if familyName is not None and familyName:
                families.add(familyName)
            else:
                print(Fore.LIGHTRED_EX + f"Warning: The file \"{fontPath}\" does not contain a valid family name. The font will be ignored." + Fore.RESET)
                return None

        exactNames = set()

        # https://docs.microsoft.com/en-us/typography/opentype/spec/name#name-ids
        # If TrueType, take "full names" which has the id 4
        # If OpenType, take "PostScript" which has the id 6
        if isTrueType:
            exactNames = fullnames
        else:
            # If not TrueType, it is OpenType
            try:
                # We use freetype like libass: https://github.com/libass/libass/blob/a2b39cde4ecb74d5e6fccab4a5f7d8ad52b2b1a4/libass/ass_fontselect.c#L326
                postscriptNameByte = freetype.Face(Path(fontPath).open("rb"), fontIndex).postscript_name
            except OSError:
                print(Fore.RED + f"Error: Please report this error on github. Attach this font \"{fontPath}\" in your issue and say that the program fail to open the font" + Fore.RESET)

            if postscriptNameByte is not None:

                try:
                    postscriptName = postscriptNameByte.decode("ASCII")
                except UnicodeDecodeError:
                    print(Fore.RED + f"Error: Please report this error on github. Attach this font \"{fontPath}\" in your issue and say that the postscript has not been correctly decoded" + Fore.RESET)

                if postscriptName:
                    exactNames.add(postscriptName)

        if "OS/2" in fontTtLib:
            try:
                # https://docs.microsoft.com/en-us/typography/opentype/spec/os2#fss
                isItalic = bool(fontTtLib["OS/2"].fsSelection & 1)

                # https://docs.microsoft.com/en-us/typography/opentype/spec/os2#usweightclass
                weight = fontTtLib['OS/2'].usWeightClass
            except struct_error:
                isItalic, weight = getFontAttributesWithFreetype(fontPath, fontIndex)
        else:
            isItalic, weight = getFontAttributesWithFreetype(fontPath, fontIndex)

        # Some font designers appear to be under the impression that weights are 1-9 (From: https://github.com/Ristellise/AegisubDC/blob/master/src/font_file_lister_coretext.mm#L70)
        if weight <= 9:
            weight *= 100

        if "fvar" in fontTtLib:
            variableName = []

            # Inpired from: https://github.com/fonttools/fonttools/discussions/2639#discussioncomment-2889678
            # I have also confirmed it by testing it
            namePrefix = getNameLikeFontConfig(16, fontTtLib['name'].names)

            if namePrefix is None:
                namePrefix = getNameLikeFontConfig(1, fontTtLib['name'].names)

            for instance in fontTtLib["fvar"].instances:
                style = fontTtLib["name"].getDebugName(instance.subfamilyNameID)
                variableName.append(namePrefix + " " + style)

            families.update(variableName)
            families.add(namePrefix)


        # The weightCompare is set to 0. It could be any value. It does not care
        fonts.append(Font(fontPath, families, weight, isItalic, Int32(0), exactNames, fontTtLib))

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
        font = createFont(fontPath)
        if font is not None:
            fontCollection.update(font)

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
    parser.add_argument('--input', '-i', nargs='*', required=True, metavar="[.ass file and/or path]", help="""
    Subtitles file. Must be an ASS file/directory. You can specify more than one .ass file/path. If no argument is specified, it will take all the font in the current path.
    """)
    parser.add_argument('-mkv', metavar="[.mkv input file]", help="""
    Video where the fonts will be merge. Must be a Matroska file.
    """)
    parser.add_argument('--output', '-o', nargs='?', const='', metavar="path", help="""
    Destination path of the font. If no argument is specified, it will be the current path.
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
            if input.endswith('.ass'):
                assFileList.append(Path(input))
            else:
                return print(Fore.RED + "Error: The input file is not an .ass file." + Fore.RESET)
        elif os.path.isdir(input):
            for file in os.listdir(input):
                if file.endswith('.ass'):
                    assFileList.append(Path(os.path.join(input, file)))
        else:
            return print(Fore.RED + "Error: The input file does not exist." + Fore.RESET)
    # Current folder. Ex: fontCollector -i -o "C:\Users\Admin\Desktop\"
    if args.input is not None and len(args.input) == 0:
        for file in os.listdir(Path()):
            if file.endswith('.ass'):
                assFileList.append(Path(file))

    for assFile in assFileList:
        print(Fore.LIGHTGREEN_EX + f"Loaded successfully {assFile.name}" + Fore.RESET)


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

    fontsUsed = findUsedFont(fontCollection, styleCollection, outputDirectory)

    if outputDirectory:
        copyFont(fontsUsed, outputDirectory)

    if mkvFile:
        if delete_fonts:
            deleteFonts(mkvFile, mkvpropedit)

        mergeFont(fontsUsed, mkvFile, mkvpropedit)


if __name__ == "__main__":
    sys.exit(main())