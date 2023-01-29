from pygame.sprite import Sprite, AbstractGroup
from pygame.surface import Surface

from fr.naulan.supermariobros.src.entities.position import Position


class Entity(Sprite):
    PLAYER = 0

    x: float
    y: float

    def __init__(self,
                 sheet: Surface,
                 position: Position,
                 *groups: AbstractGroup):
        super().__init__(*groups)

        self.x = position.x
        self.y = position.y

        if sheet is not None:
            self.image = sheet
            self.rect = self.image.get_rect()
