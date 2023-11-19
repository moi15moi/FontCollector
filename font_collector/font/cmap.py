from __future__ import annotations

class CMap:
    """
    Represent a CMap table. It doesn't contain all the information of a CMap.
    https://learn.microsoft.com/en-us/typography/opentype/spec/cmap
    """

    platform_id: int
    platform_enc_id: int

    def __init__(
        self: CMap,
        platform_id: int,
        platform_enc_id: int,
    ):
        self.platform_id = platform_id
        self.platform_enc_id = platform_enc_id


    def __eq__(self: CMap, other: CMap):
        return (self.platform_id, self.platform_enc_id) == (other.platform_id, other.platform_enc_id)


    def __hash__(self: CMap):
        return hash((self.platform_id, self.platform_enc_id))


    def __repr__(self: CMap):
        return f'CMap(Platform ID="{self.platform_id}", Platform encoding ID="{self.platform_enc_id}")'