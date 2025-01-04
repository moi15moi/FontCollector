import os

from fontTools.ttLib.ttFont import TTFont

dir_path = os.path.dirname(os.path.realpath(__file__))

font = TTFont(os.path.join(dir_path, "Alegreya - Original.ttf"))
font.saveXML(os.path.join(dir_path, "Alegreya - Original.xml"))

axis_value = font["STAT"].table.AxisValueArray.AxisValue[1]
# Set the ValueNameID to an NameID that doesn't exist
axis_value.ValueNameID = 70

font.save(os.path.join(dir_path, "Test #13.ttf"))
font.saveXML(os.path.join(dir_path, "Test #13.xml"))
