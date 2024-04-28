from fontTools.ttLib.ttFont import TTFont
from fontTools.ttLib.tables._n_a_m_e import NameRecord

import os

dir_path = os.path.dirname(os.path.realpath(__file__))

font = TTFont(os.path.join(dir_path, "Alegreya - Original.ttf"))
font.saveXML(os.path.join(dir_path, "Alegreya - Original.xml"))

name_records = []
for axis_value in font["STAT"].table.AxisValueArray.AxisValue:
    name_id = axis_value.ValueNameID

    for name in font["name"].names:
        if name.nameID == name_id and name_id not in (275, 262):
            name_record = NameRecord()
            name_record.nameID = name.nameID
            name_record.string = f"{name.string.decode('utf_16_be')} French Canada"
            name_record.platformID = name.platformID
            name_record.platEncID = name.platEncID
            name_record.langID = 0x0C0C

            name_records.append(name_record)
        if name.nameID in (275, 262):
            name.langID = 0x0C0C


font["name"].names.extend(name_records)

name_record = NameRecord()
name_record.nameID = 16
name_record.string = "family text".encode('utf_16_be')
name_record.platformID = name.platformID
name_record.platEncID = name.platEncID
name_record.langID = 0x0C0C
font["name"].names.append(name_record)


font.save(os.path.join(dir_path, "Test #9.ttf"))
font.saveXML(os.path.join(dir_path, "Test #9.xml"))
