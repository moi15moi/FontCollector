from font_collector.font_parser import FontParser
from fontTools.ttLib.tables._n_a_m_e import NameRecord


def test_fallback_encoding():
    # The string are from the font in this pack: https://github.com/libass/libass/issues/643#issuecomment-1476459274

    # 微软简标宋 - PlatEncID 3.TTF
    name_record = NameRecord()
    name_record.nameID = 1
    name_record.string = b'\x00\xce\x00\xa2\x00\xc8\x00\xed\x00\xbc\x00\xf2\x00\xb1\x00\xea\x00\xcb\x00\xce'
    name_record.platformID = 3
    name_record.platEncID = 3
    name_record.langID = 0
    FontParser.get_decoded_name(name_record) == "微软简标宋"

    # 文鼎中特廣告體 - PlatEncID 4.ttf
    name_record = NameRecord()
    name_record.nameID = 1
    name_record.string = b'\x00\xa4\x00\xe5\x00\xb9\x00\xa9\x00\xa4\x00\xa4\x00\xaf\x00S\x00\xbc\x00s\x00\xa7\x00i\x00\xc5\x00\xe9'
    name_record.platformID = 3
    name_record.platEncID = 4
    name_record.langID = 0
    FontParser.get_decoded_name(name_record) == "文鼎中特廣告體"