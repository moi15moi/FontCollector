import collections
import os
import pytest
import string
from font_collector import PlatformID
from font_collector.font.cmap import CMap
from langcodes import Language
from typing import Hashable

dir_path = os.path.dirname(os.path.realpath(__file__))


def test__init__():
    platform_id = PlatformID.MACINTOSH
    platform_enc_id = 0

    cmap = CMap(platform_id, platform_enc_id)

    assert cmap.platform_id == platform_id
    assert cmap.platform_enc_id == platform_enc_id


def test__repr__():
    platform_id = PlatformID.MACINTOSH
    platform_enc_id = 0

    cmap = CMap(platform_id, platform_enc_id)
    assert repr(cmap) == 'CMap(Platform ID="1", Platform encoding ID="0")'
