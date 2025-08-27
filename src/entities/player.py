from pygame.sprite import Sprite

from ..sprite_animation import SpriteAnimation
from ..inputs.ressources import Ressources
from ..tile import Tile


class Player(Sprite):
    def __init__(self, group, vector):
        super().__init__(group)
        self.image = Ressources()["images"]["mario"].subsurface(
            (0, 0), (Tile.WIDTH, Tile.HEIGHT)
        )
        self.rect = self.image.get_rect(topleft=vector)
        self.rect.update(
            self.rect.left, self.rect.top, self.rect.width - 1, self.rect.height - 1
        )
        self.vector = vector
        
        self.current_animation = SpriteAnimation.Undefined
        self.levels_animation = SpriteAnimation(
            self,
            Ressources()["images"]["mario"].subsurface(
                (Tile.WIDTH * 3, Tile.HEIGHT * 2), (Tile.WIDTH, Tile.HEIGHT * 2)
            ),
            2,
            1.5,
            "y",
        )

    def update(self, dt):
        self.current_animation.update(dt)
        self.rect.update(self.vector.x, self.vector.y, Tile.WIDTH - 1, Tile.HEIGHT - 1)
