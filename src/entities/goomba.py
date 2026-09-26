from __future__ import annotations

from pygame import Surface

from .entity import Entity, Level


class Goomba(Entity):
    """Walks towards Mario, falls from ledges and turns around at walls.

    Stomping it squashes it; touching it from the side hurts Mario.
    """

    ANIMATIONS = ("walk", "squashed")
    ENEMY = True
    SPEED = 32.0
    SQUASHED_DURATION = 0.5

    def __init__(self, *args):
        super().__init__(*args)
        self.squashed = False
        self.squashed_time = 0.0

    @property
    def alive(self) -> bool:
        return super().alive and not self.squashed

    def behave(self, dt: float, level: Level) -> None:
        if self.squashed:
            self.squashed_time += dt
            self.removed = self.squashed_time >= self.SQUASHED_DURATION
            return
        self.walk(dt, level, self.SPEED)

    def touch_mario(self, level: Level, stomp: bool) -> None:
        if stomp:
            self.squashed = True
            self.body.vx = 0.0
            level.stomped(self)
        else:
            level.hurt_mario()

    def image(self) -> Surface:
        if self.squashed:
            return self.animations["squashed"].image()
        return self.animations["walk"].image(self.time)
