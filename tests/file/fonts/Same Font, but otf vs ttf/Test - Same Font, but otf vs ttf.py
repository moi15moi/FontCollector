from fontTools.ttLib.ttFont import TTFont
import os

# Test if GDI perfer OTF VS TTF file when family, weight and italic is the same
# Conclusion: It prefer TTF file over OTF file


dir_path = os.path.dirname(os.path.realpath(__file__))
font = TTFont(os.path.join(dir_path, "Alivia.ttf"))

cmap = font["cmap"].getcmap(3, 1)
cmap.cmap[ord("A")] = "B"
font["name"].setName("Alivia Regular V2", 4, 3, 1, 0x409) # set a different fullname name


font.save(os.path.join(dir_path, "Alivia - Generated.ttf"))

