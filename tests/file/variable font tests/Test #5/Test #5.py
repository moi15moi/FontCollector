import os

from fontTools.ttLib.tables import otTables
from fontTools.ttLib.ttFont import TTFont

dir_path = os.path.dirname(os.path.realpath(__file__))

font = TTFont(os.path.join(dir_path, "Alegreya - Original.ttf"))
font.saveXML(os.path.join(dir_path, "Alegreya - Original.xml"))

# Change this AxisValue range, so the NamedInstance can match to the AxisValue Format 4
font["STAT"].table.AxisValueArray.AxisValue[3].RangeMinValue = 750
font["STAT"].table.AxisValueArray.AxisValue[3].RangeMaxValue = 750


# Add an AxisValue 4 with multiple AxisValue in the AxisValueRecord
axis_value = otTables.AxisValue()
axis_value.Format = 4
axis_value.Flags = 0
axis_value.ValueNameID = 256
axis_value.AxisCount = 2

axis_value.AxisValueRecord = []
for tag, value in (("wght", 800), ("ital", 1)):
    rec = otTables.AxisValueRecord()
    rec.AxisIndex = next(
        i
        for i, a in enumerate(font["STAT"].table.DesignAxisRecord.Axis)
        if a.AxisTag == tag
    )
    rec.Value = value
    axis_value.AxisValueRecord.append(rec)

font["STAT"].table.AxisValueArray.AxisValue.insert(0, axis_value)


font.save(os.path.join(dir_path, "Test #5.ttf"))
font.saveXML(os.path.join(dir_path, "Test #5.xml"))
