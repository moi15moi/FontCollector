import os

from fontTools.ttLib.ttFont import TTFont

dir_path = os.path.dirname(os.path.realpath(__file__))

font = TTFont(os.path.join(dir_path, "Alegreya - Original.ttf"))
font.saveXML(os.path.join(dir_path, "Alegreya - Original.xml"))

# Change the AxisValue of ExtraBold, so when loading the NamedInstance wght = 800, it won't match to this AxisValue. It will match to the AxisValue 900
font["STAT"].table.AxisValueArray.AxisValue[3].RangeMinValue = 870
font["STAT"].table.AxisValueArray.AxisValue[3].RangeMaxValue = 880
font.save(os.path.join(dir_path, "Test #8.ttf"))
font.saveXML(os.path.join(dir_path, "Test #8.xml"))
