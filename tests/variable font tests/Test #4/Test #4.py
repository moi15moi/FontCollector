from fontTools.ttLib.ttFont import TTFont
from fontTools.ttLib.tables import otTables
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

font = TTFont(os.path.join(dir_path, "Alegreya - Original.ttf"))
font.saveXML(os.path.join(dir_path, "Alegreya - Original.xml"))

# Add an AxisValue 4 with only 1 AxisValue in the AxisValueRecord
axis_value = otTables.AxisValue()
axis_value.Format = 4
axis_value.Flags = 0
axis_value.ValueNameID = 256
axis_value.AxisCount = 2

axis_value.AxisValueRecord = []
for tag, value in (("wght", 800),):
    rec = otTables.AxisValueRecord()
    rec.AxisIndex = next(
        i
        for i, a in enumerate(font["STAT"].table.DesignAxisRecord.Axis)
        if a.AxisTag == tag
    )
    rec.Value = value
    axis_value.AxisValueRecord.append(rec)

font["STAT"].table.AxisValueArray.AxisValue.insert(0, axis_value)


font.save(os.path.join(dir_path, "Test #4.ttf"))
font.saveXML(os.path.join(dir_path, "Test #4.xml"))
