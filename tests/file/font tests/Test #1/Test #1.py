import os

from fontTools.ttLib.ttFont import TTFont

dir_path = os.path.dirname(os.path.realpath(__file__))

font = TTFont(os.path.join(dir_path, "F5AJJI3A.TTF"))
font.saveXML(os.path.join(dir_path, "F5AJJI3A - Original.xml"))

name_record = font["name"].getName(1, 3, 2)
name_record.string = b"example"

font.save(os.path.join(dir_path, "Test #1.ttf"))
font.saveXML(os.path.join(dir_path, "Test #1.xml"))

# GDI decode the name : "數慭灬"
# It ignore the error when decoding: b"example".decode("utf_16_be", "ignore")
