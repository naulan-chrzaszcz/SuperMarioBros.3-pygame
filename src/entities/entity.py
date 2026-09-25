"""Base class of the enemies and items of a platform level.

An entity only knows the level through the small :class:`Level` interface,
implemented by ``PlatformLevelScene``: adding a new kind of entity does not
require to change the scene (see CONTRIBUTING.md).
"""

from __future__ import annotations

from typing import Dict, Protocol, Tuple

from pygame import Rect, Surface, transform

from ..constants import TILE_HEIGHT, TILE_WIDTH
from ..platformer import Body
from .catalog import Palette, recolored

Frame = Dict[int, Surface]  # facing (-1 left, 1 right) -> image


class Level(Protocol):
    """What an entity can see and do in the level it lives in."""

    mario: Body
    height: int

    def is_solid(self, column: int, row: int) -> bool: ...

    def hurt_mario(self) -> None: ...

    def stomped(self, entity: "Entity") -> None:
        """Mario jumped on ``entity``: he bounces and scores the stomp chain."""

    def score(self, points: int, x: float, y: float) -> None: ...

    def grow_mario(self, x: float, y: float) -> None: ...

    def add_life(self, x: float, y: float) -> None: ...


class Sprites:
    """Frames cut in the images of ``ressources.yaml``, facing both ways."""

    def __init__(self, ressources):
        self.ressources = ressources
        self._frames: Dict[Tuple, Frame] = {}

    def frame(self, image: str, rect: Tuple[int, int, int, int], palette: Palette = ()) -> Frame:
        """The sheets draw the entities facing left."""
        key = (image, tuple(rect), palette)
        if key not in self._frames:
            left = recolored(self.ressources.image(image).subsurface(rect), palette)
            self._frames[key] = {-1: left, 1: transform.flip(left, True, False)}
        return self._frames[key]


class Entity:
    """Something that lives in a level: it sleeps until Mario comes close."""

    TYPE = ""
    WIDTH = 14
    HEIGHT = 15
    # Enemies hurt Mario, can be stomped and are knocked out by kicked shells.
    ENEMY = False
    KNOCK_SPEED = 220.0
    KNOCK_POINTS = 100

    def __init__(self, sprites: Sprites, column: int, row: int):
        self.sprites = sprites
        self.column = column
        self.row = row
        # Standing on the bottom of its cell, centered.
        self.body = Body(
            column * TILE_WIDTH + (TILE_WIDTH - self.WIDTH) / 2,
            (row + 1) * TILE_HEIGHT - self.HEIGHT,
            self.WIDTH,
            self.HEIGHT,
        )
        self.direction = -1
        self.active = False
        self.removed = False
        self.knocked = False
        # Drawn under the tiles, e.g. an item coming out of a block.
        self.behind_tiles = False
        # Mario cannot touch it for a moment (just stomped or kicked).
        self.ignore_mario = 0.0
        self.time = 0.0

    @property
    def rect(self) -> Rect:
        return self.body.rect

    @property
    def alive(self) -> bool:
        """Can still touch Mario or be touched by a shell."""
        return self.active and not self.removed and not self.knocked

    def activate(self, level: Level) -> None:
        """Mario comes close: the entity starts moving towards him."""
        self.active = True
        self.direction = 1 if level.mario.center_x > self.body.center_x else -1

    def update(self, dt: float, level: Level) -> None:
        self.time += dt
        self.ignore_mario = max(0.0, self.ignore_mario - dt)
        if self.knocked:
            self.body.fall(dt)
            self.body.x += self.body.vx * dt
            self.body.y += self.body.vy * dt
        if self.body.y > level.height + TILE_HEIGHT * 2:
            self.removed = True

    def walk(self, dt: float, level: Level, speed: float) -> None:
        """Walks straight on, falls from ledges and turns around at walls."""
        body = self.body
        body.vx = self.direction * speed
        body.fall(dt)
        body.move(dt, level.is_solid)
        if body.hit_wall:
            self.direction = -self.direction

    def turn_around(self) -> None:
        self.direction = -self.direction

    def touch_mario(self, level: Level, stomp: bool) -> None:
        """Mario touches the entity; ``stomp`` when he falls on its head."""

    def knock(self, level: Level, direction: int) -> None:
        """Hit by a shell or by a block bumped under it: it flips and falls off
        the screen."""
        if self.knocked:
            return
        self.knocked = True
        self.body.vx = direction * 50.0
        self.body.vy = -self.KNOCK_SPEED
        level.score(self.KNOCK_POINTS, self.body.center_x, self.body.y)

    def image(self) -> Surface:
        raise NotImplementedError

    def draw(self, surface: Surface, camera_x: float, camera_y: float) -> None:
        image = self.image()
        if self.knocked:
            image = transform.flip(image, False, True)
        x = self.body.center_x - image.get_width() / 2 - camera_x
        y = self.body.bottom - image.get_height() - camera_y
        surface.blit(image, (round(x), round(y)))
