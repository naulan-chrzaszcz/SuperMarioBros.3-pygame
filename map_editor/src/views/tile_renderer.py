"""Renderer for tileset cells and animated map tiles."""

from __future__ import annotations

from typing import Dict, Tuple

import pygame

from ..constants import ANIMATION_SPEED, TILE_SIZE
from ..models.tileset import Tileset
from ..outputs.tile import Tile

PLACEHOLDER_COLOR = (255, 0, 255)


class TileRenderer:
    """Builds (and caches) the zoomed, rotated and animated image of a tile."""

    MAX_CACHE_SIZE = 4096

    def __init__(self, tileset: Tileset) -> None:
        self.tileset = tileset
        self._cache: Dict[Tuple[int, int, int, int], pygame.Surface] = {}

    @staticmethod
    def frame_index(tile: Tile, time: float) -> int:
        if tile.frames <= 1:
            return 0
        return int(time * ANIMATION_SPEED) % tile.frames

    def render(self, tile: Tile, size: int, time: float = 0.0) -> pygame.Surface:
        frame = self.frame_index(tile, time)
        if tile.frames == 1 and (tile.x, tile.y) in self.tileset.animations:
            x, y = self.tileset.animations[(tile.x, tile.y)][
                int(time * ANIMATION_SPEED) % len(self.tileset.animations[(tile.x, tile.y)])
            ]
        else:
            x = tile.x + (frame if tile.x_frames > 1 else 0)
            y = tile.y + (frame if tile.y_frames > 1 else 0)
        key = (x, y, tile.rotation, size)

        surface = self._cache.get(key)
        if surface is None:
            surface = self._build(x, y, tile.rotation, size)
            if len(self._cache) >= self.MAX_CACHE_SIZE:
                self._cache.clear()
            self._cache[key] = surface
        return surface

    def _build(self, x: int, y: int, rotation: int, size: int) -> pygame.Surface:
        surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        if self.tileset.contains(x, y):
            source = self.tileset.image.subsurface(
                (x * TILE_SIZE, y * TILE_SIZE), (TILE_SIZE, TILE_SIZE)
            ).copy()
            source.set_colorkey(self.tileset.image.get_colorkey())
            surface.blit(source, (0, 0))
        else:
            surface.fill(PLACEHOLDER_COLOR)
        surface = pygame.transform.rotate(surface, rotation)
        return pygame.transform.scale(surface, (size, size))
