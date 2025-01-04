import os

from fontTools.ttLib.ttFont import TTFont
from fontTools.varLib.instancer.names import ELIDABLE_AXIS_VALUE_NAME

dir_path = os.path.dirname(os.path.realpath(__file__))

font = TTFont(os.path.join(dir_path, "AdventPro - Original.ttf"))
font.saveXML(os.path.join(dir_path, "AdventPro - Original.xml"))

# Change version to 1.0
font['STAT'].table.Version = 0x00010000
del font['STAT'].table.ElidedFallbackNameID

for axis_value in font["STAT"].table.AxisValueArray.AxisValue:
    axis_value.Flags = ELIDABLE_AXIS_VALUE_NAME


font.save(os.path.join(dir_path, "Test #11.ttf"))
font.saveXML(os.path.join(dir_path, "Test #11.xml"))
