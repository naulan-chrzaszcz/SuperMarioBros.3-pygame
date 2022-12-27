from dataclasses import dataclass
from typing import Tuple, List


@dataclass
class TileData:
    tile_code: int
    colors: List[Tuple[int, int, int], ...] = None
