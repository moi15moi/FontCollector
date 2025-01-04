import os

from fontTools.ttLib.ttFont import TTFont

dir_path = os.path.dirname(os.path.realpath(__file__))

font = TTFont(os.path.join(dir_path, "AdventPro - Original.ttf"))
font.saveXML(os.path.join(dir_path, "AdventPro - Original.xml"))

# Test a font that contain an STAT table, but doesn't contain an FVAR table
del font["gvar"]
del font["fvar"]

font["OS/2"].usWeightClass = 300
font["OS/2"].fsSelection = 0b1


font.save(os.path.join(dir_path, "Test #3.ttf"))
font.saveXML(os.path.join(dir_path, "Test #3.xml"))
