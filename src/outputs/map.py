from typing import Dict, Tuple

import json

from pygame import Rect

from .tile import Tile


class Map:
    TILE_COORD_SEPARATOR = ","
    TILE_FRAMES_SEPARATOR = "+"
    TILE_ROTATION_SEPARATOR = "&"

    @staticmethod
    def write(
        file_name: str,
        tiles: Dict[Tuple[int, int], Tile],
        collidables: Dict[Tuple[int, int], Rect],
        width_map: int,
        height_map: int,
    ):
        map_data = {}
        map_data["tiles"] = [
            ["-1,-1" for _ in range(width_map // 16)] for _ in range(height_map // 16)
        ]
        map_data["collidables"] = [
            [False for _ in range(width_map // 16)] for _ in range(height_map // 16)
        ]

        for pos, tile in tiles.items():
            x = int(pos[0] // 16)
            y = int(pos[1] // 16)
            tile_data = f"{int(tile.x)}"
            if tile.x_frames > 1:
                tile_data += f"{Map.TILE_FRAMES_SEPARATOR}{tile.x_frames}"
            tile_data += f"{Map.TILE_COORD_SEPARATOR}{int(tile.y)}"
            if tile.y_frames > 1:
                tile_data += f"{Map.TILE_FRAMES_SEPARATOR}{tile.y_frames}"
            if tile.rotation > 0:
                tile_data += f"{Map.TILE_ROTATION_SEPARATOR}{tile.rotation // 90}"
            map_data["tiles"][y][x] = tile_data

        for pos, _ in collidables.items():
            x = int(pos[0] // 16)
            y = int(pos[1] // 16)
            map_data["collidables"][y][x] = True

        with open(file_name, "w") as file:
            json.dump(map_data, file)
