from pygame.sprite import Sprite


class Entity(Sprite):
    PLAYER = 0

    x: float
    y: float

    def __init__(self, sheet, position, *groups):
        super().__init__(*groups)

        self.x = position.x
        self.y = position.y

