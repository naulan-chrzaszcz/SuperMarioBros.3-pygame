from pygame.sprite import Sprite, AbstractGroup
from pygame.surface import Surface

from src.entities.position import Position


class Entity(Sprite):
    PLAYER: int = 0

    x: float
    y: float

    def __init__(self,
                 sheet: Surface,
                 position: Position,
                 groups: AbstractGroup):
        Sprite.__init__(self, groups)

        self.x = position.x
        self.y = position.y

        if sheet is not None:
            self.image = sheet
            self.rect = self.image.get_rect()
