from __future__ import annotations
from .name import PlatformID

class CMap:
    """
    Represent a CMap table. It doesn't contain all the information of a CMap.
    https://learn.microsoft.com/en-us/typography/opentype/spec/cmap
    """

    def __init__(
        self: CMap,
        platform_id: PlatformID,
        platform_enc_id: int,
    ) -> None:
        self.platform_id = platform_id
        self.platform_enc_id = platform_enc_id


    def __eq__(self: CMap, other: object):
        if not isinstance(other, CMap):
            return False
        return (self.platform_id, self.platform_enc_id) == (other.platform_id, other.platform_enc_id)


    def __hash__(self: CMap):
        return hash((self.platform_id, self.platform_enc_id))


    def __repr__(self: CMap):
        return f'{self.__class__.__name__}(Platform ID="{self.platform_id}", Platform encoding ID="{self.platform_enc_id}")'