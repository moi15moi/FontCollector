from fontTools.ttLib.ttFont import TTFont
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

font = TTFont(os.path.join(dir_path, "Alegreya - Original.ttf"))
font.saveXML(os.path.join(dir_path, "Alegreya - Original.xml"))

# Remove all the AxisValue
font["STAT"].table.AxisValueArray.AxisValue = []

# Change the weight class and the font to italic
font["OS/2"].usWeightClass = 300
font["OS/2"].fsSelection = 0b1

font.save(os.path.join(dir_path, "Test #2.ttf"))
font.saveXML(os.path.join(dir_path, "Test #2.xml"))
