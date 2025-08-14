from pygame import Rect, Surface, Vector2


class Tile:
    WIDTH = 16
    HEIGHT = 16

    def __init__(
        self, tile: Surface, vector: Vector2, tile_width=WIDTH, tile_height=HEIGHT
    ):
        self.tile = tile
        self.vector = vector
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.rect = Rect(vector.x, vector.y, tile_width, tile_height)

    def draw(self, surface: Surface):
        surface.blit(self.tile, self.vector)
