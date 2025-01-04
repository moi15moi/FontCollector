from collections.abc import Hashable

from font_collector import PlatformID
from font_collector.font.cmap import CMap


def test__init__():
    platform_id = PlatformID.MACINTOSH
    platform_enc_id = 0

    cmap = CMap(platform_id, platform_enc_id)

    assert cmap.platform_id == platform_id
    assert cmap.platform_enc_id == platform_enc_id

def test__eq__():
    cmap_1 = CMap(3, 1)
    cmap_2 = CMap(3, 1)
    assert cmap_1 == cmap_2

    cmap_3 = CMap(3, 2)
    assert cmap_1 != cmap_3

    cmap_4 = CMap(1, 1)
    assert cmap_1 != cmap_4

    assert cmap_1 != 1

def test__hash__():
    cmap_1 = CMap(3, 1)
    cmap_2 = CMap(3, 1)

    assert isinstance(cmap_1, Hashable)
    assert {cmap_1} == {cmap_2}

    cmap_3 = CMap(3, 2)
    assert {cmap_1} != {cmap_3}

    cmap_4 = CMap(1, 1)
    assert {cmap_1} != {cmap_4}


def test__repr__():
    platform_id = PlatformID.MACINTOSH
    platform_enc_id = 0

    cmap = CMap(platform_id, platform_enc_id)
    assert repr(cmap) == 'CMap(Platform ID="1", Platform encoding ID="0")'
