import pytest
from font_collector.font.chinese_variant import ChineseVariant
from langcodes import Language


def test_from_lang_code():
    assert ChineseVariant.from_lang_code(Language.get("zh-Hans")) == ChineseVariant.SIMPLIFIED
    assert ChineseVariant.from_lang_code(Language.get("zh")) == ChineseVariant.SIMPLIFIED
    assert ChineseVariant.from_lang_code(Language.get("zh-CN")) == ChineseVariant.SIMPLIFIED
    assert ChineseVariant.from_lang_code(Language.get("zh-SG")) == ChineseVariant.SIMPLIFIED
    assert ChineseVariant.from_lang_code(Language.get("zh-Hant")) == ChineseVariant.TRADITIONAL
    assert ChineseVariant.from_lang_code(Language.get("zh-HK")) == ChineseVariant.TRADITIONAL
    assert ChineseVariant.from_lang_code(Language.get("zh-MO")) == ChineseVariant.TRADITIONAL
    assert ChineseVariant.from_lang_code(Language.get("zh-TW")) == ChineseVariant.TRADITIONAL

    with pytest.raises(ValueError) as exc_info:
        ChineseVariant.from_lang_code(Language.get("en"))
    assert str(exc_info.value) == f"The language {Language.get('en')} isn't chinese."
