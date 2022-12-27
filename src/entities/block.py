from abc import abstractmethod

from pygame import Surface
from pygame.sprite import Sprite


class Block(Sprite):
    image: Surface

    def __init__(self, game, group_sprite, image):
        Sprite.__init__(self, group_sprite)
        self.image = image
        self.game = game

    @abstractmethod
    def update(self, *args, **kwargs) -> None:
        pass
