from enum import Enum

from src.maps_engine.tile_data import TileData


class Tiles(Enum):
    EMPTY = TileData(-1)
    PLATFORM = TileData(1, [])
    FLOORS = 2
    BUSH = 3
    LOOT_BLOCK = 4
    CLOUD = 5
