import os
import pytest
from font_collector import InvalidNameRecord, Name, PlatformID
from font_collector.font.lcid import WINDOWS_LCID_CODE_TO_LANGUAGES
from fontTools.ttLib.tables._n_a_m_e import NameRecord, _MAC_LANGUAGES
from langcodes import Language
from typing import Hashable

dir_path = os.path.dirname(os.path.realpath(__file__))


def test__init__():
    value = "test"
    lang_code = Language.get("en")
    name = Name(value=value, lang_code=lang_code)

    assert value == name.value
    assert lang_code == name.lang_code


def test_from_name_record():
    expected_value = "Example"
    expected_lang_code = Language.get("en-US")

    name_record = NameRecord()
    name_record.nameID = 1
    name_record.string = expected_value.encode("utf_16_be")
    name_record.platformID = 3
    name_record.platEncID = 1
    name_record.langID = 0x409

    assert Name.from_name_record(name_record) == Name(expected_value, expected_lang_code)


def test_get_name_encoding():
    name_record = NameRecord()
    name_record.platformID = 3
    name_record.platEncID = 0
    assert Name.get_name_record_encoding(name_record) == "utf_16_be"

    name_record = NameRecord()
    name_record.platformID = 3
    name_record.platEncID = 1
    assert Name.get_name_record_encoding(name_record) == "utf_16_be"

    name_record = NameRecord()
    name_record.platformID = 3
    name_record.platEncID = 2
    assert Name.get_name_record_encoding(name_record) == "utf_16_be"

    name_record = NameRecord()
    name_record.platformID = 3
    name_record.platEncID = 6
    assert Name.get_name_record_encoding(name_record) == "utf_16_be"

    name_record = NameRecord()
    name_record.platformID = 3
    name_record.platEncID = 10
    assert Name.get_name_record_encoding(name_record) == "utf_16_be"

    name_record = NameRecord()
    name_record.platformID = 3
    name_record.platEncID = 3
    assert Name.get_name_record_encoding(name_record) == "cp936"

    name_record = NameRecord()
    name_record.nameID = 1
    name_record.platformID = 3
    name_record.platEncID = 4
    assert Name.get_name_record_encoding(name_record) == "cp950"

    name_record = NameRecord()
    name_record.nameID = 2
    name_record.platformID = 3
    name_record.platEncID = 4
    assert Name.get_name_record_encoding(name_record) == "utf_16_be"

    name_record = NameRecord()
    name_record.nameID = 1
    name_record.platformID = 3
    name_record.platEncID = 5
    assert Name.get_name_record_encoding(name_record) == "cp949"

    name_record = NameRecord()
    name_record.nameID = 2
    name_record.platformID = 3
    name_record.platEncID = 5
    assert Name.get_name_record_encoding(name_record) == "utf_16_be"

    name_record = NameRecord()
    name_record.platformID = 1
    name_record.platEncID = 0
    assert Name.get_name_record_encoding(name_record) == "iso-8859-1"

    name_record = NameRecord()
    name_record.platformID = 1
    name_record.platEncID = 1
    assert Name.get_name_record_encoding(name_record) == None

    name_record = NameRecord()
    name_record.platformID = 0
    assert Name.get_name_record_encoding(name_record) == None


def test_get_decoded_name():
    # The string are from the font in this pack: https://github.com/libass/libass/issues/643#issuecomment-1476459274

    # 微软简标宋 - PlatEncID 3.TTF
    name_record = NameRecord()
    name_record.nameID = 1
    name_record.string = b"\x00\xce\x00\xa2\x00\xc8\x00\xed\x00\xbc\x00\xf2\x00\xb1\x00\xea\x00\xcb\x00\xce"
    name_record.platformID = 3
    name_record.platEncID = 3
    name_record.langID = 0
    Name.get_decoded_name_record(name_record) == "微软简标宋"

    # 文鼎中特廣告體 - PlatEncID 4.ttf
    name_record = NameRecord()
    name_record.nameID = 1
    name_record.string = b"\x00\xa4\x00\xe5\x00\xb9\x00\xa9\x00\xa4\x00\xa4\x00\xaf\x00S\x00\xbc\x00s\x00\xa7\x00i\x00\xc5\x00\xe9"
    name_record.platformID = 3
    name_record.platEncID = 4
    name_record.langID = 0
    Name.get_decoded_name_record(name_record) == "文鼎中特廣告體"

    # tests\font tests\Test #1\Test #1.ttf
    name_record = NameRecord()
    name_record.nameID = 1
    name_record.string = b"example"
    name_record.platformID = 3
    name_record.platEncID = 2
    name_record.langID = 0
    Name.get_decoded_name_record(name_record) == "數慭灬"

    # tests\fonts\font_cmap_encoding_2.TTF
    name_record = NameRecord()
    name_record.nameID = 1
    name_record.string = b'\x00F\x00j0\xa40\xfc0\xde\x003\x001\x000'
    name_record.platformID = 3
    name_record.platEncID = 2
    name_record.langID = 1041
    Name.get_decoded_name_record(name_record) == "Fjイーマ310"

    # tests\fonts\font_mac.TTF
    name_record = NameRecord()
    name_record.nameID = 1
    name_record.string = b'Brushstroke Plain'
    name_record.platformID = 1
    name_record.platEncID = 0
    name_record.langID = 0
    Name.get_decoded_name_record(name_record) == "Brushstroke Plain"

    # https://github.com/libass/libass/issues/679#issuecomment-1442262479
    name_record = NameRecord()
    name_record.nameID = 1
    name_record.string = "Test®".encode("macroman")
    name_record.platformID = 1
    name_record.platEncID = 0
    name_record.langID = 0
    Name.get_decoded_name_record(name_record) == "Test¨"

    name_record.nameID = 1
    name_record.string = b"anything"
    name_record.platformID = 1
    name_record.platEncID = 1
    name_record.langID = 0
    with pytest.raises(InvalidNameRecord) as exc_info:
        Name.get_decoded_name_record(name_record)
    assert str(exc_info.value) == "The NameRecord you provided isn't supported by GDI: NameRecord(PlatformID=1, PlatEncID=1, LangID=0, String=b'anything', NameID=1)"


def test_get_lang_code_of_namerecord():
    name_record = NameRecord()
    name_record.platformID = 3
    name_record.langID = 0
    Name.get_lang_code_of_namerecord(name_record) == "und"

    name_record = NameRecord()
    name_record.platformID = 3
    name_record.langID = 0x409
    Name.get_lang_code_of_namerecord(name_record) == "en"

    name_record = NameRecord()
    name_record.platformID = 1
    name_record.langID = 0
    Name.get_lang_code_of_namerecord(name_record) == "en"

    name_record = NameRecord()
    name_record.platformID = 1
    name_record.langID = 160
    Name.get_lang_code_of_namerecord(name_record) == "und"

    name_record = NameRecord()
    name_record.platformID = 0
    Name.get_lang_code_of_namerecord(name_record) == "und"


def test_get_lang_code_platform_code():
    name = Name("test", Language.get("en-US"))
    assert 0x409 == name.get_lang_id_from_platform_id(PlatformID.MICROSOFT)
    assert 0 == name.get_lang_id_from_platform_id(PlatformID.MACINTOSH)

    invalid_language_code = Name("test", Language.get("en-fr"))
    with pytest.raises(ValueError) as exc_info:
        invalid_language_code.get_lang_id_from_platform_id(PlatformID.MICROSOFT)
    assert str(exc_info.value) == 'The lang_code "en-FR" isn\'t supported by the microsoft platform'
    assert Language.get(WINDOWS_LCID_CODE_TO_LANGUAGES[invalid_language_code.get_lang_id_from_platform_id(PlatformID.MICROSOFT, True)]).language == "en"

    with pytest.raises(ValueError) as exc_info:
        invalid_language_code.get_lang_id_from_platform_id(PlatformID.MACINTOSH)
    assert str(exc_info.value) == 'The lang_code "en-FR" isn\'t supported by the macintosh platform'
    assert Language.get(_MAC_LANGUAGES[invalid_language_code.get_lang_id_from_platform_id(PlatformID.MACINTOSH, True)]).language == "en"

    with pytest.raises(ValueError) as exc_info:
        invalid_language_code.get_lang_id_from_platform_id(10)
    assert str(exc_info.value) == 'You cannot specify the platform id 10. You can only specify the microsoft or the macintosh id'

    name = Name("test", Language.get("qaa"))
    with pytest.raises(ValueError) as exc_info:
        name.get_lang_id_from_platform_id(PlatformID.MACINTOSH)
    assert str(exc_info.value) == 'The lang_code "qaa" isn\'t supported by the macintosh platform'


def test__eq__():
    name_1 = Name("the value", Language.get("en"))
    name_2 = Name("the value", Language.get("en"))
    assert name_1 == name_2

    name_3 = Name("no", Language.get("en"))
    assert name_1 != name_3

    name_4 = Name("the value", Language.get("fr"))
    assert name_1 != name_4

    assert name_1 != "test"

def test__hash__():
    name_1 = Name("the value", Language.get("en"))
    name_2 = Name("the value", Language.get("en"))
    assert isinstance(name_1, Hashable)
    assert {name_1} == {name_2}

    name_3 = Name("no", Language.get("en"))
    assert {name_1} != {name_3}

    name_4 = Name("the value", Language.get("fr"))
    assert {name_1} != {name_4}

    assert {name_1} != {"test"}


def test__repr__():
    name = Name("the value", Language.get("en"))
    assert repr(name) == 'Name(value="the value", lang_code="en")'
