from __future__ import annotations

from .name import PlatformID


class CMap:
    """Represents a CMap table. It doesn't contain all the information of a CMap.
    https://learn.microsoft.com/en-us/typography/opentype/spec/cmap

    Attributes:
        platform_id: The platform ID of the CMap.
        platform_enc_id: The platform encoding ID of the CMap.
    """

    def __init__(
        self,
        platform_id: PlatformID,
        platform_enc_id: int,
    ) -> None:
        self.platform_id = platform_id
        self.platform_enc_id = platform_enc_id


    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CMap):
            return False
        return (self.platform_id, self.platform_enc_id) == (other.platform_id, other.platform_enc_id)


    def __hash__(self) -> int:
        return hash((self.platform_id, self.platform_enc_id))


    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(Platform ID="{self.platform_id}", Platform encoding ID="{self.platform_enc_id}")'
