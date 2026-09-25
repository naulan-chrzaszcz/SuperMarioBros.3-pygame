from __future__ import annotations

from pygame import Surface

from .entity import Entity, Level, Sprites


class Goomba(Entity):
    """Walks towards Mario, falls from ledges and turns around at walls.

    Stomping it squashes it; touching it from the side hurts Mario.
    """

    TYPE = "goomba"
    ENEMY = True
    SPEED = 32.0
    STEP_DURATION = 0.15  # the walk is the frame flipped back and forth
    SQUASHED_DURATION = 0.5

    def __init__(self, sprites: Sprites, column: int, row: int):
        super().__init__(sprites, column, row)
        self.walking = sprites.frame("goomba", (0, 0, 16, 16))
        self.flat = sprites.frame("goomba", (16, 0, 16, 16))[-1]
        self.squashed = False
        self.squashed_time = 0.0

    @property
    def alive(self) -> bool:
        return super().alive and not self.squashed

    def update(self, dt: float, level: Level) -> None:
        super().update(dt, level)
        if self.knocked:
            return
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
            return self.flat
        return self.walking[1 if int(self.time / self.STEP_DURATION) % 2 else -1]
