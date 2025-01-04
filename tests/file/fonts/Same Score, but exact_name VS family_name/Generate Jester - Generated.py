import os

from fontTools.ttLib.ttFont import TTFont

# Test if GDI perfer exact_name match over family_name when same score is the same
# Conclusion: It prefer first installed font


dir_path = os.path.dirname(os.path.realpath(__file__))
font = TTFont(os.path.join(dir_path, "Jester.ttf"))

cmap = font["cmap"].getcmap(3, 1)
cmap.cmap[ord("A")] = "B"
font["name"].setName("Jester Regular", 1, 3, 1, 0x409) # set Family name
font["name"].setName("Jester Regular V2", 4, 3, 1, 0x409) # set Fullname name


font.save(os.path.join(dir_path, "Jester - Generated.ttf"))
