from __future__ import annotations

from pygame import Surface, Vector2
from pygame.sprite import Sprite

from ..sprite_animation import SpriteAnimation
from ..tile import Tile


class Player(Sprite):
    def __init__(self, group, vector, sheet: Surface):
        super().__init__(group)
        self.image = sheet.subsurface((0, 0), (Tile.WIDTH, Tile.HEIGHT))
        self.vector = Vector2(vector)
        self.rect = self.image.get_rect(topleft=self.vector)

        self.levels_animation = SpriteAnimation(
            self,
            sheet.subsurface((Tile.WIDTH * 3, Tile.HEIGHT * 2), (Tile.WIDTH, Tile.HEIGHT * 2)),
            2,
            1.5,
            "y",
        )
        self.current_animation: SpriteAnimation | None = None

    def play(self, animation: SpriteAnimation | None) -> None:
        self.current_animation = animation
        if animation is not None:
            animation.reset()

    def update(self, dt: float) -> None:
        if self.current_animation is not None:
            self.current_animation.update(dt)
        self.rect.topleft = (round(self.vector.x), round(self.vector.y))
