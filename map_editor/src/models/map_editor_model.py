from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Tuple

import pygame

from ..constantes import TILE_SIZE
from ..outputs.map import Map
from ..outputs.tile import Tile


@dataclass
class MapEditorModel:
    width: int
    height: int
    sheet: pygame.Surface
    tiles: Dict[Tuple[int, int], Tile] = field(default_factory=dict)
    collidables: Dict[Tuple[int, int], pygame.Rect] = field(default_factory=dict)
    tile_selection_x: int = 0
    tile_selection_y: int = 0
    dirty: bool = False

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Map dimensions must be positive")
        if self.width % TILE_SIZE or self.height % TILE_SIZE:
            raise ValueError("Map dimensions must be multiples of the tile size")

    def add_tile(self, col: int, row: int, tile: Tile) -> None:
        self._validate_cell(col, row)
        self.tiles[(col * TILE_SIZE, row * TILE_SIZE)] = tile
        self.dirty = True

    def remove_tile(self, col: int, row: int) -> None:
        if self.tiles.pop((col * TILE_SIZE, row * TILE_SIZE), None) is not None:
            self.dirty = True

    def set_collidable(self, col: int, row: int, value: bool) -> None:
        self._validate_cell(col, row)
        pos = (col * TILE_SIZE, row * TILE_SIZE)
        if value:
            if pos in self.collidables:
                return
            self.collidables[pos] = pygame.Rect(*pos, TILE_SIZE, TILE_SIZE)
        else:
            if self.collidables.pop(pos, None) is None:
                return
        self.dirty = True

    def load(self, path: Path) -> None:
        data = Map.read(path)
        rows = len(data["tiles"])
        columns = len(data["tiles"][0])
        if columns * TILE_SIZE != self.width or rows * TILE_SIZE != self.height:
            raise ValueError(
                f"Map file is {columns}x{rows} tiles, expected "
                f"{self.width // TILE_SIZE}x{self.height // TILE_SIZE}"
            )

        loaded_tiles = {}
        loaded_collidables = {}
        for row, tiles in enumerate(data["tiles"]):
            for col, tile_data in enumerate(tiles):
                tile = Map.decode_tile(tile_data)
                if tile is None:
                    continue
                self._validate_sheet_tile(tile)
                tile.surface = self.create_tile_surface(tile)
                loaded_tiles[(col * TILE_SIZE, row * TILE_SIZE)] = tile

        for row, collidables in enumerate(data["collidables"]):
            for col, collidable in enumerate(collidables):
                if collidable:
                    loaded_collidables[(col * TILE_SIZE, row * TILE_SIZE)] = (
                        pygame.Rect(
                            col * TILE_SIZE,
                            row * TILE_SIZE,
                            TILE_SIZE,
                            TILE_SIZE,
                        )
                    )
        self.tiles = loaded_tiles
        self.collidables = loaded_collidables
        self.dirty = False

    def create_tile_surface(self, tile: Tile) -> pygame.Surface:
        self._validate_sheet_tile(tile)
        return pygame.transform.rotate(
            self.sheet.subsurface(
                (tile.x * TILE_SIZE, tile.y * TILE_SIZE),
                (TILE_SIZE, TILE_SIZE),
            ).copy(),
            tile.rotation,
        )

    def _validate_cell(self, col: int, row: int) -> None:
        if not 0 <= col < self.width // TILE_SIZE:
            raise ValueError(f"Column is outside the map: {col}")
        if not 0 <= row < self.height // TILE_SIZE:
            raise ValueError(f"Row is outside the map: {row}")

    def _validate_sheet_tile(self, tile: Tile) -> None:
        sheet_columns = self.sheet.get_width() // TILE_SIZE
        sheet_rows = self.sheet.get_height() // TILE_SIZE
        if not 0 <= tile.x < sheet_columns or not 0 <= tile.y < sheet_rows:
            raise ValueError(f"Tile coordinates are outside the tileset: {tile.x},{tile.y}")
        if tile.x + tile.x_frames > sheet_columns:
            raise ValueError("Horizontal animation frames exceed the tileset")
        if tile.y + tile.y_frames > sheet_rows:
            raise ValueError("Vertical animation frames exceed the tileset")
