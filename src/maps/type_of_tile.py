from enum import Enum


class TypeOfTile(Enum):
    EMPTY: int = -1
    PLATFORM: int = 1
    FLOORS: int = 2
    BUSH: int = 3
    LOOT_BLOCK: int = 4
    CLOUD: int = 5
