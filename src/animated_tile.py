from pygame import Surface, Vector2

from .tile import Tile


class AnimatedTile(Tile):
    def __init__(
        self,
        tile: Surface,
        vector: Vector2,
        frames: int,
        speed=1.5,
        subsurface_direction="x",
        tile_width=Tile.WIDTH,
        tile_height=Tile.HEIGHT,
    ):
        super().__init__(tile, vector, tile_width, tile_height)
        self.frames = frames
        self.speed = speed
        self.subsurface_direction = subsurface_direction
        self.timer = 0

    def draw(self, surface: Surface) -> None:
        if self.subsurface_direction == "x":
            surface.blit(
                self.tile.subsurface(
                    (int(self.timer) * self.tile_width, 0),
                    (self.tile_width, self.tile_height),
                ),
                self.vector,
            )
        elif self.subsurface_direction == "y":
            surface.blit(
                self.tile.subsurface(
                    (0, int(self.timer) * self.tile_height),
                    (self.tile_width, self.tile_height),
                ),
                self.vector,
            )

    def update(self, dt: float) -> None:
        self.timer += self.speed * dt
        self.timer %= self.frames
