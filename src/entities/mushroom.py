from __future__ import annotations

from pygame import Surface

from ..constants import TILE_HEIGHT
from .catalog import entity_types
from .entity import Entity, Level, Sprites


class Mushroom(Entity):
    """A Super Mushroom: makes Mario big.

    Placed on a solid block, it is hidden inside and comes out when Mario hits
    the block from below. It then slides away, falls from ledges and turns
    around at walls.
    """

    TYPE = "mushroom"
    WIDTH = 16
    HEIGHT = 16
    SPEED = 60.0
    EMERGE_DURATION = 0.6
    HOP_SPEED = 180.0

    def __init__(self, sprites: Sprites, column: int, row: int):
        super().__init__(sprites, column, row)
        palette = entity_types()[self.TYPE].palette if self.TYPE in entity_types() else ()
        self.picture = sprites.frame("mushroom", (0, 0, 16, 16), palette)[-1]
        self.hidden = False
        self.emerging = 0.0

    def hide(self) -> None:
        """Puts the item inside the block of its cell."""
        self.hidden = True

    def activate(self, level: Level) -> None:
        if self.hidden:
            return
        self.active = True
        self.direction = 1

    def emerge(self) -> None:
        """Its block was hit: the item rises out of it."""
        self.hidden = False
        self.active = True
        self.direction = 1
        self.emerging = self.EMERGE_DURATION
        self.behind_tiles = True

    def update(self, dt: float, level: Level) -> None:
        super().update(dt, level)
        if self.emerging > 0:
            self.emerging = max(0.0, self.emerging - dt)
            progress = 1 - self.emerging / self.EMERGE_DURATION
            self.body.y = (self.row - progress) * TILE_HEIGHT
            self.behind_tiles = self.emerging > 0
            return
        self.walk(dt, level, self.SPEED)

    @property
    def alive(self) -> bool:
        return super().alive and self.emerging <= 0

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
        return self.picture


class OneUp(Mushroom):
    """A green mushroom: one more life."""

    TYPE = "one_up"

    def collect(self, level: Level) -> None:
        level.add_life(self.body.center_x, self.body.y)
