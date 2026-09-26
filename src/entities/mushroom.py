from __future__ import annotations

from pygame import Surface

from .entity import Entity, Level


class Mushroom(Entity):
    """A Super Mushroom: makes Mario big.

    Placed on a solid block, it is hidden inside and comes out when Mario hits
    the block from below. It then slides away, falls from ledges and turns
    around at walls.
    """

    ANIMATIONS = ("idle",)
    WIDTH = 16
    HEIGHT = 16
    CAN_HIDE = True
    SPEED = 60.0
    HOP_SPEED = 180.0

    def activate(self, level: Level) -> None:
        if self.hidden:
            return
        self.active = True
        self.direction = 1

    def behave(self, dt: float, level: Level) -> None:
        self.walk(dt, level, self.SPEED)

    def touch_mario(self, level: Level, stomp: bool) -> None:
        self.removed = True
        self.collect(level)

    def collect(self, level: Level) -> None:
        level.grow_mario(self.body.center_x, self.body.y)

    def knock(self, level: Level, direction: int) -> None:
        """The block under it was hit: it hops."""
        self.body.vy = -self.HOP_SPEED
        self.body.on_ground = False

    def image(self) -> Surface:
        return self.animations["idle"].image(self.time)


class OneUp(Mushroom):
    """A green mushroom: one more life."""

    def collect(self, level: Level) -> None:
        level.add_life(self.body.center_x, self.body.y)
