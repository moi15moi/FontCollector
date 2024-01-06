from langcodes import Language
from font_collector.font.chinese_variant import ChineseVariant


def test_from_lang_code():
    assert ChineseVariant.from_lang_code(Language.get("zh-Hans")) == ChineseVariant.SIMPLIFIED
    assert ChineseVariant.from_lang_code(Language.get("zh")) == ChineseVariant.SIMPLIFIED
    assert ChineseVariant.from_lang_code(Language.get("zh-CN")) == ChineseVariant.SIMPLIFIED
    assert ChineseVariant.from_lang_code(Language.get("zh-SG")) == ChineseVariant.SIMPLIFIED
    assert ChineseVariant.from_lang_code(Language.get("zh-Hant")) == ChineseVariant.TRADITIONAL
    assert ChineseVariant.from_lang_code(Language.get("zh-HK")) == ChineseVariant.TRADITIONAL
    assert ChineseVariant.from_lang_code(Language.get("zh-MO")) == ChineseVariant.TRADITIONAL
    assert ChineseVariant.from_lang_code(Language.get("zh-TW")) == ChineseVariant.TRADITIONAL