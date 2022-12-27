from abc import abstractmethod

from pygame.sprite import Sprite, LayeredUpdates

from src.game import Game
from src.position import Position


class Upgrade(Sprite):
    game: Game
    x: float
    y: float

    def __init__(self,
                 group_sprites: LayeredUpdates,
                 game: Game,
                 position: Position) -> None:
        Sprite.__init__(self, group_sprites)
        self.game = game
        self.x = position.x
        self.y = position.y

    @abstractmethod
    def apply(self) -> None:
        pass

    @abstractmethod
    def update(self, *args, **kwargs) -> None:
        pass
