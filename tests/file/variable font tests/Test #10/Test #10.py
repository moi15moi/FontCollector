from fontTools.ttLib.ttFont import TTFont
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

font = TTFont(os.path.join(dir_path, "Alegreya - Original.ttf"))
font.saveXML(os.path.join(dir_path, "Alegreya - Original.xml"))

axis_value = font["STAT"].table.AxisValueArray.AxisValue[1]
# Set the AxisIndex to an index that doesn't exist
axis_value.AxisIndex = len(font["STAT"].table.DesignAxisRecord.Axis)

font.save(os.path.join(dir_path, "Test #10.ttf"))
font.saveXML(os.path.join(dir_path, "Test #10.xml"))
