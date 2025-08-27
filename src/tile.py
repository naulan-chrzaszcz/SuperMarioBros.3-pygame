from pygame import Surface, Vector2
from pygame.sprite import Sprite

from .sprite_animation import SpriteAnimation


class Tile(Sprite):
    WIDTH = 16
    HEIGHT = 16

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
        self.vector = vector
        self.collidable = collidable
        self.rect = self.image.get_rect(topleft=vector)
        self.animation = SpriteAnimation.Undefined

    def set_animation(self, animation):
        self.animation = animation

    def update(self, dt: float) -> None:
        self.animation.update(dt)
