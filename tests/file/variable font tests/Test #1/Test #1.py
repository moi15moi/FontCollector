import os

from fontTools.ttLib.ttFont import TTFont

dir_path = os.path.dirname(os.path.realpath(__file__))

font = TTFont(os.path.join(dir_path, "AdventPro - Original.ttf"))
font.saveXML(os.path.join(dir_path, "AdventPro - Original.xml"))

# Set the first axes defaultValue to a value not in [minValue, maxValue]
font["fvar"].axes[0].defaultValue = font["fvar"].axes[0].maxValue + 1


font.save(os.path.join(dir_path, "Test #1.ttf"))
font.saveXML(os.path.join(dir_path, "Test #1.xml"))
