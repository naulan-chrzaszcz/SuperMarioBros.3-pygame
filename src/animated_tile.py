from pygame import Surface, Vector2
from pygame.sprite import Sprite

from .tile import Tile


class AnimatedTile(Sprite):
    def __init__(
        self,
        group,
        tile: Surface,
        vector: Vector2,
        frames: int,
        speed=1.5,
        subsurface_direction="x",
        tile_width=Tile.WIDTH,
        tile_height=Tile.HEIGHT,
        collidable=False,
    ):
        Sprite.__init__(self, group)
        self.tile = tile
        self.image = tile.subsurface((0, 0), (tile_width, tile_height))
        self.rect = self.image.get_rect(topleft=vector)
        self.vector = vector
        self.frames = frames
        self.speed = speed
        self.subsurface_direction = subsurface_direction
        self.timer = 0
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.collidable = collidable

    def update(self, dt: float) -> None:
        self.timer += self.speed * dt
        self.timer %= self.frames

        if self.subsurface_direction == "x":
            self.image = self.tile.subsurface(
                (int(self.timer) * self.tile_width, 0),
                (self.tile_width, self.tile_height),
            )
        elif self.subsurface_direction == "y":
            self.image = self.tile.subsurface(
                (0, int(self.timer) * self.tile_height),
                (self.tile_width, self.tile_height),
            )
