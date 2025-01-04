import os

from fontTools.ttLib.ttFont import TTFont

dir_path = os.path.dirname(os.path.realpath(__file__))

font = TTFont(os.path.join(dir_path, "AdventPro - Original.ttf"))
font.saveXML(os.path.join(dir_path, "AdventPro - Original.xml"))

# Remove all the AxisValue like the Test #2
font["STAT"].table.AxisValueArray.AxisValue = []

# Invalid NameID
font["STAT"].table.ElidedFallbackNameID = 500


font.save(os.path.join(dir_path, "Test #6.ttf"))
font.saveXML(os.path.join(dir_path, "Test #6.xml"))
