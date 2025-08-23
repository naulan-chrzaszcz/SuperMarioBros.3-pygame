from pygame import Surface, Vector2
from pygame.sprite import Sprite


class Tile(Sprite):
    WIDTH = 16
    HEIGHT = 16

    def __init__(self, group, tile: Surface, vector: Vector2):
        Sprite.__init__(self, group)
        self.image = tile
        self.vector = vector
        self.rect = self.image.get_rect(topleft=vector)
