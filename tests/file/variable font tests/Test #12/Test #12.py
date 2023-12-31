from fontTools.ttLib.ttFont import TTFont
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

font = TTFont(os.path.join(dir_path, "font_without axis_value - Original.ttf"))
font.saveXML(os.path.join(dir_path, "font_without axis_value - Original.xml"))

font['STAT'].table.DesignAxisCount = 0
del font['STAT'].table.DesignAxisRecord

# Don't try to open the font on windows. It seems that any application that use GDI or DirectWrite won't work correctly.
font.save(os.path.join(dir_path, "Test #12.ttf"))
font.saveXML(os.path.join(dir_path, "Test #12.xml"))
