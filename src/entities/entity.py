"""Base class of the enemies and items of a platform level.

An entity only knows the level through the small :class:`Level` interface,
implemented by ``PlatformLevelScene``: adding a new kind of entity does not
require to change the scene (see CONTRIBUTING.md).

Everything that can be tuned is data: the pictures are the ``animations`` of
the entity in ``res/entities.yaml`` and its ``settings`` override the
UPPER_CASE constants of its class (``speed: 40`` sets ``SPEED``).
"""

from __future__ import annotations

from typing import Dict, Protocol, Tuple

from pygame import Rect, Surface, transform

from ..animation import Animation, SpriteBank
from ..constants import TILE_HEIGHT, TILE_WIDTH
from ..inputs.tuning import tune
from ..platformer import Body
from .catalog import EntityType


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

    def play_sound(self, name: str) -> None: ...


class Entity:
    """Something that lives in a level: it sleeps until Mario comes close."""

    # Animations the class needs in res/entities.yaml.
    ANIMATIONS: Tuple[str, ...] = ()
    NOT_TUNABLE = ("ANIMATIONS",)

    WIDTH = 14
    HEIGHT = 15
    # Enemies hurt Mario, can be stomped and are knocked out by kicked shells.
    ENEMY = False
    # Walking entities turn around at the edge of a floor instead of falling.
    TURN_AT_LEDGES = False
    # Placed on a solid block (a ? block), it hides inside until the block is hit.
    CAN_HIDE = False
    EMERGE_DURATION = 0.6
    GRAVITY = Body.GRAVITY
    KNOCK_SPEED = 220.0
    KNOCK_POINTS = 100

    def __init__(self, kind: EntityType, sprites: SpriteBank, column: int, row: int):
        self.kind = kind
        tune(self, kind.settings, f"entities.yaml: {kind.id}")
        self.animations: Dict[str, Animation] = sprites.build(
            kind.image, kind.animations, kind.facing, kind.palette, kind.id
        )
        missing = [name for name in self.ANIMATIONS if name not in self.animations]
        if missing:
            raise ValueError(f"entities.yaml: {kind.id} needs the animation(s) {', '.join(missing)}")
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
        self.hidden = False
        self.emerging = 0.0
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
        return self.active and not self.removed and not self.knocked and self.emerging <= 0

    def activate(self, level: Level) -> None:
        """Mario comes close: the entity starts moving towards him."""
        if self.hidden:
            return
        self.active = True
        self.direction = 1 if level.mario.center_x > self.body.center_x else -1

    def hide(self) -> None:
        """Puts the entity inside the block of its cell."""
        self.hidden = True

    def emerge(self) -> None:
        """Its block was hit: the entity rises out of it, then comes to life."""
        self.hidden = False
        self.active = True
        self.direction = 1
        self.emerging = self.EMERGE_DURATION
        self.behind_tiles = True

    def update(self, dt: float, level: Level) -> None:
        self.time += dt
        self.ignore_mario = max(0.0, self.ignore_mario - dt)
        if self.knocked:
            self.body.fall(dt, self.GRAVITY)
            self.body.x += self.body.vx * dt
            self.body.y += self.body.vy * dt
        elif self.emerging > 0:
            self.emerging = max(0.0, self.emerging - dt)
            progress = 1 - self.emerging / self.EMERGE_DURATION
            self.body.y = (self.row + 1) * TILE_HEIGHT - self.body.height - progress * TILE_HEIGHT
            self.behind_tiles = self.emerging > 0
        else:
            self.behave(dt, level)
        if self.body.y > level.height + TILE_HEIGHT * 2:
            self.removed = True

    def behave(self, dt: float, level: Level) -> None:
        """What the entity does on each frame once it is awake."""

    def walk(self, dt: float, level: Level, speed: float) -> None:
        """Walks straight on, falls from ledges (or turns back, with
        ``TURN_AT_LEDGES``) and turns around at walls."""
        body = self.body
        if self.TURN_AT_LEDGES and body.on_ground and speed and self._ledge_ahead(level):
            self.direction = -self.direction
        body.vx = self.direction * speed
        body.fall(dt, self.GRAVITY)
        body.move(dt, level.is_solid)
        if body.hit_wall:
            self.direction = -self.direction

    def _ledge_ahead(self, level: Level) -> bool:
        body = self.body
        front = body.x + body.width + 1 if self.direction > 0 else body.x - 1
        column = int(front // TILE_WIDTH)
        row = int((body.bottom + 1) // TILE_HEIGHT)
        return not level.is_solid(column, row)

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
        level.play_sound("kick")

    def image(self) -> Surface:
        raise NotImplementedError

    def draw(self, surface: Surface, camera_x: float, camera_y: float) -> None:
        image = self.image()
        if self.knocked:
            image = transform.flip(image, False, True)
        x = self.body.center_x - image.get_width() / 2 - camera_x
        y = self.body.bottom - image.get_height() - camera_y
        surface.blit(image, (round(x), round(y)))
