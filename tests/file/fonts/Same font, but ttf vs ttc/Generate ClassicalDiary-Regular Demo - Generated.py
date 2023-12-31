from fontTools.ttLib.ttFont import TTFont
from fontTools.ttLib.ttCollection import TTCollection
import os

# Test if GDI perfer TTF VS TTC file when family, weight and italic is the same
# Conclusion: It prefer first installed font


dir_path = os.path.dirname(os.path.realpath(__file__))
font = TTFont(os.path.join(dir_path, "ClassicalDiary-Regular Demo.ttf"))

cmap = font["cmap"].getcmap(3, 1)
cmap.cmap[ord("A")] = "B"
font["name"].setName("ClassicalDiary V2", 4, 3, 1, 0x409) # set Fullname name


font_collection = TTCollection()
font_collection.fonts.append(font)
font_collection.save(os.path.join(dir_path, "ClassicalDiary-Regular Demo - Generated.ttc"))
