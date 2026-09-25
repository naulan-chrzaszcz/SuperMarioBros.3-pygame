import json
import re
from pathlib import Path
from typing import Dict, Optional, Tuple

from pygame import Rect

from ..constantes import TILE_SIZE
from .tile import Tile


class Map:
    TILE_COORD_SEPARATOR = ","
    TILE_FRAMES_SEPARATOR = "+"
    TILE_ROTATION_SEPARATOR = "&"
    TILE_PATTERN = re.compile(
        r"^(?P<x>-?\d+)(?:\+(?P<x_frames>\d+))?,"
        r"(?P<y>-?\d+)(?:\+(?P<y_frames>\d+))?"
        r"(?:&(?P<rotation>[0-3]))?$"
    )

    @classmethod
    def decode_tile(cls, value: str) -> Optional[Tile]:
        if not isinstance(value, str):
            raise ValueError("Tile entries must be strings")

        match = cls.TILE_PATTERN.fullmatch(value)
        if match is None:
            raise ValueError(f"Invalid tile entry: {value!r}")

        x = int(match.group("x"))
        y = int(match.group("y"))
        if (x, y) == (-1, -1):
            if value != "-1,-1":
                raise ValueError("Empty tiles must use the exact value '-1,-1'")
            return None
        if x < 0 or y < 0:
            raise ValueError(f"Tile coordinates cannot be negative: {value!r}")

        x_frames = int(match.group("x_frames") or 1)
        y_frames = int(match.group("y_frames") or 1)
        if x_frames < 1 or y_frames < 1:
            raise ValueError(f"Animation frame counts must be positive: {value!r}")
        if x_frames > 1 and y_frames > 1:
            raise ValueError(f"A tile can animate on only one axis: {value!r}")

        return Tile(
            x,
            y,
            x_frames,
            y_frames,
            int(match.group("rotation") or 0) * 90,
        )

    @classmethod
    def encode_tile(cls, tile: Tile) -> str:
        if tile.x < 0 or tile.y < 0:
            raise ValueError("Tile coordinates cannot be negative")
        if tile.x_frames < 1 or tile.y_frames < 1:
            raise ValueError("Animation frame counts must be positive")
        if tile.x_frames > 1 and tile.y_frames > 1:
            raise ValueError("A tile can animate on only one axis")
        if tile.rotation not in (0, 90, 180, 270):
            raise ValueError("Tile rotation must be 0, 90, 180, or 270 degrees")

        tile_data = str(tile.x)
        if tile.x_frames > 1:
            tile_data += f"{cls.TILE_FRAMES_SEPARATOR}{tile.x_frames}"
        tile_data += f"{cls.TILE_COORD_SEPARATOR}{tile.y}"
        if tile.y_frames > 1:
            tile_data += f"{cls.TILE_FRAMES_SEPARATOR}{tile.y_frames}"
        if tile.rotation:
            tile_data += f"{cls.TILE_ROTATION_SEPARATOR}{tile.rotation // 90}"
        return tile_data

    @classmethod
    def read(cls, file_name: Path) -> dict:
        with Path(file_name).open(encoding="utf-8") as file:
            map_data = json.load(file)

        if not isinstance(map_data, dict):
            raise ValueError("Map data must be a JSON object")
        tiles = map_data.get("tiles")
        collidables = map_data.get("collidables")
        if not isinstance(tiles, list) or not tiles:
            raise ValueError("Map 'tiles' must be a non-empty matrix")
        if not isinstance(collidables, list) or len(collidables) != len(tiles):
            raise ValueError("Map 'collidables' must have the same rows as 'tiles'")

        width = len(tiles[0])
        if width == 0:
            raise ValueError("Map rows cannot be empty")
        for row_index, (tile_row, collidable_row) in enumerate(
            zip(tiles, collidables)
        ):
            if not isinstance(tile_row, list) or len(tile_row) != width:
                raise ValueError(f"Tile row {row_index} has an invalid width")
            if not isinstance(collidable_row, list) or len(collidable_row) != width:
                raise ValueError(f"Collidable row {row_index} has an invalid width")
            for tile_data in tile_row:
                cls.decode_tile(tile_data)
            if any(not isinstance(value, bool) for value in collidable_row):
                raise ValueError(
                    f"Collidable row {row_index} must contain only booleans"
                )
        return map_data

    @classmethod
    def write(
        cls,
        file_name: Path,
        tiles: Dict[Tuple[int, int], Tile],
        collidables: Dict[Tuple[int, int], Rect],
        width_map: int,
        height_map: int,
    ) -> None:
        if width_map <= 0 or height_map <= 0:
            raise ValueError("Map dimensions must be positive")
        if width_map % TILE_SIZE or height_map % TILE_SIZE:
            raise ValueError("Map dimensions must be multiples of the tile size")

        width = width_map // TILE_SIZE
        height = height_map // TILE_SIZE
        map_data = {
            "tiles": [["-1,-1" for _ in range(width)] for _ in range(height)],
            "collidables": [[False for _ in range(width)] for _ in range(height)],
        }

        for pos, tile in tiles.items():
            x = pos[0] // TILE_SIZE
            y = pos[1] // TILE_SIZE
            if not 0 <= x < width or not 0 <= y < height:
                raise ValueError(f"Tile position is outside the map: {pos}")
            map_data["tiles"][y][x] = cls.encode_tile(tile)

        for pos in collidables:
            x = pos[0] // TILE_SIZE
            y = pos[1] // TILE_SIZE
            if not 0 <= x < width or not 0 <= y < height:
                raise ValueError(f"Collidable position is outside the map: {pos}")
            map_data["collidables"][y][x] = True

        path = Path(file_name)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = path.with_name(f"{path.name}.tmp")
        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(map_data, file, separators=(",", ":"))
        temporary_path.replace(path)
