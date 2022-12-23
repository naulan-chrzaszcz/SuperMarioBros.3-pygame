from abc import abstractmethod

from pygame.rect import Rect
from pygame.sprite import Sprite
from pygame.surface import Surface

from src.game import Game


class Entity(Sprite):
    game: Game

    look: int  # -1 left, 1 right
    offset: list  # [0] left, right & [1] up, down
    velocity: float

    top_collision: bool
    bottom_collision: bool
    right_collision: bool
    left_collision: bool

    x: float
    y: float

    image: Surface
    rect: Rect

    def __init__(self,
                 game: Game,
                 x: float,
                 y: float,
                 velocity: float) -> None:
        super(Entity, self).__init__()
        self.game = game
        self.x = x
        self.y = y
        self.velocity = velocity

        self.look = 0
        self.offset = [0, 0]
        self.top_collision = False
        self.bottom_collision = False
        self.right_collision = False
        self.left_collision = False

    @staticmethod
    def palette_swap(surf, old_c, new_c):
        img_copy = Surface(surf.get_size())
        img_copy.fill(new_c)
        surf.set_colorkey(old_c)
        img_copy.blit(surf, (0, 0))
        return img_copy

    @abstractmethod
    def update(self, *args, **kwargs) -> None:
        pass

    def apply_an_image(self, img: Surface) -> None:
        self.image = img

        width = self.image.get_width()
        height = self.image.get_height()
        self.rect = Rect(self.x, self.y, width, height)

    def move_left(self) -> None:
        self.look = -1
        self.x -= self.velocity * self.game.dt

    def move_right(self) -> None:
        pass
