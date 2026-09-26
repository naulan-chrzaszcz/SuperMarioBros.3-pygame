from __future__ import annotations

from pygame import Vector2
from pygame.sprite import Sprite

from ..animation import Animation, Animator


class Player(Sprite):
    """Mario on the world map and on the world card: the ``world_mario``
    animations of ``res/sprites.yaml``."""

    def __init__(self, group, vector, animation: Animation):
        super().__init__(group)
        self.image = animation.frame(0)
        self.vector = Vector2(vector)
        self.rect = self.image.get_rect(topleft=self.vector)
        self.levels_animation = Animator(self, animation)
        self.current_animation: Animator | None = None

    def play(self, animation: Animator | None) -> None:
        self.current_animation = animation
        if animation is not None:
            animation.reset()

    def update(self, dt: float) -> None:
        if self.current_animation is not None:
            self.current_animation.update(dt)
        self.rect.topleft = (round(self.vector.x), round(self.vector.y))
