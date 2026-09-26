"""One tile of a map, as a pygame sprite (optionally animated)."""

from __future__ import annotations

from typing import Optional

from pygame import Surface, Vector2
from pygame.sprite import Sprite

from .constants import TILE_HEIGHT, TILE_WIDTH
from .sprite_animation import SpriteAnimation


class Tile(Sprite):
    """One cell of a map; ``id`` is its tile name in the tileset metadata."""

    WIDTH = TILE_WIDTH
    HEIGHT = TILE_HEIGHT

    def __init__(
        self,
        group,
        id: str,
        tile: Surface,
        vector: Vector2,
        tile_width=WIDTH,
        tile_height=HEIGHT,
        collidable=False,
    ):
        Sprite.__init__(self, group)
        self.id = id
        self.image = tile.subsurface((0, 0), (tile_width, tile_height))
        self.vector = Vector2(vector)
        self.collidable = collidable
        self.rect = self.image.get_rect(topleft=self.vector)
        self.animation: Optional[SpriteAnimation] = None

    @property
    def cell(self) -> tuple[int, int]:
        """Column and row of the tile in its map."""
        return int(self.vector.x) // self.WIDTH, int(self.vector.y) // self.HEIGHT

    def set_animation(self, animation: Optional[SpriteAnimation]) -> None:
        self.animation = animation

    def update(self, dt: float) -> None:
        if self.animation is not None:
            self.animation.update(dt)
        self.rect.topleft = (round(self.vector.x), round(self.vector.y))
