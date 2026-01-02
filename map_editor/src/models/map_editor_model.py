import json
import pygame

from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Tuple

from src.constantes import TILE_SIZE
from src.outputs.tile import Tile
from src.outputs.map import Map


@dataclass
class MapEditorModel:
    width: int
    height: int
    sheet: pygame.Surface
    tiles = Dict[Tuple[int, int], Tile] = field(default_factory=dict)
    collidables: Dict[Tuple[int, int], pygame.Rect] = field(default_factory=dict)
    tile_selection_x = 0
    tile_selection_y = 0

    def add_tile(self, col: int, row: int, tile: Tile) -> None:
        self.tiles[(col * TILE_SIZE, row * TILE_SIZE)] = tile

    def remove_tile(self, col: int, row: int) -> None:
        self.tiles.pop((col * TILE_SIZE, row * TILE_SIZE), None)

    def set_collidable(self, col: int, row: int, value: bool) -> None:
        pos = (col * TILE_SIZE, row * TILE_SIZE)
        if value:
            self.collidables[pos] = pygame.Rect(*pos, TILE_SIZE, TILE_SIZE)
        else:
            self.collidables.pop(pos, None)

    def load(self, path: Path, sheet) -> None:
        with path.open() as f:
            data = json.load(f)

        for row, tiles in enumerate(data["tiles"]):
            for col, tile in enumerate(tiles):
                sheet_x, sheet_y = tile.split(Map.TILE_COORD_SEPARATOR)
            frames_x = "1"
            if sheet_x.count("+") == 1:
                sheet_x, frames_x = sheet_x.split("+")
            frames_y = "1"
            if sheet_y.count("+") == 1:
                sheet_y, frames_y = sheet_y.split("+")
            rotation = "0"
            if sheet_y.count("&") == 1:
                sheet_y, rotation = sheet_y.split("&")
            if frames_y.count("&") == 1:
                frames_y, rotation = frames_y.split("&")

            if sheet_x == "-1" and sheet_y == "-1":
                continue

            tile = Tile(
                int(sheet_x),
                int(sheet_y),
                int(frames_x),
                int(frames_y),
                int(rotation) * 90,
            )
            tile.surface = pygame.transform.rotate(
                sheet.subsurface(
                    (tile.x * TILE_SIZE, tile.y * TILE_SIZE),
                    (TILE_SIZE, TILE_SIZE),
                ).copy(),
                int(rotation) * 90,
            )
            self.tiles[(col * TILE_SIZE, row * TILE_SIZE)] = tile

        for row, collidables in enumerate(data["collidables"]):
            for col, collidable in enumerate(collidables):
                if collidable:
                    self.collidables[(col * TILE_SIZE, row * TILE_SIZE)] = (
                            pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                        )

