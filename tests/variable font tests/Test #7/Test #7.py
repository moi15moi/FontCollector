from fontTools.ttLib.ttFont import TTFont
from fontTools.ttLib.tables import otTables
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

font = TTFont(os.path.join(dir_path, "Alegreya - Original.ttf"))
font.saveXML(os.path.join(dir_path, "Alegreya - Original.xml"))


# Change this AxisValue, so for the NamedInstance "wght" == 800, it will take the AxisValue Format 4 weight and the AxisValue Format 1 "ital".
font["STAT"].table.AxisValueArray.AxisValue[3].NominalValue = 755
font["STAT"].table.AxisValueArray.AxisValue[3].RangeMinValue = 750
font["STAT"].table.AxisValueArray.AxisValue[3].RangeMaxValue = 760

# Add an AxisValue 4 with multiple AxisValue in the AxisValueRecord
axis_value = otTables.AxisValue()
axis_value.Format = 4
axis_value.Flags = 0
axis_value.ValueNameID = 256
axis_value.AxisCount = 2

axis_value.AxisValueRecord = []
for tag, value in (("wght", 800), ("ital", 2)):
    rec = otTables.AxisValueRecord()
    rec.AxisIndex = next(
        i
        for i, a in enumerate(font["STAT"].table.DesignAxisRecord.Axis)
        if a.AxisTag == tag
    )
    rec.Value = value
    axis_value.AxisValueRecord.append(rec)

font["STAT"].table.AxisValueArray.AxisValue.insert(0, axis_value)

# Change the ElidedFallbackNameID, so the ElidedName is not "italic". This is simply to not create problem with the AxisValue Format 1 "ital" which is also named "italic".
font["STAT"].table.ElidedFallbackNameID = 11


font.save(os.path.join(dir_path, "Test #7.ttf"))
font.saveXML(os.path.join(dir_path, "Test #7.xml"))
