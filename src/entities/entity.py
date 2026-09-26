"""Base class of the enemies and items of a platform level.

An entity only knows the level through the small :class:`Level` interface,
implemented by ``PlatformLevelScene``: adding a new kind of entity does not
require to change the scene (see CONTRIBUTING.md).

Everything that can be tuned is data: the pictures are the ``animations`` of
the entity in ``res/entities.yaml`` and its ``settings`` override the
UPPER_CASE constants of its class (``speed: 40`` sets ``SPEED``).

Its *behaviour* is data too. What the entity does is a set of named effects
chosen by a setting: ``movement`` (how it moves), ``onStomp`` and ``onTouch``
(what Mario touching it does), ``onKnock`` (a shell or a bumped block hit it),
``onWake`` (where it looks when it comes to life) and ``collect`` (the reward
of a collected item). Each name is a method of the class, so a file cannot
call anything else and a typo is reported with the list of the known names.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional, Protocol, Tuple

from pygame import Rect, Surface, transform

from ..animation import Animation, SpriteBank
from ..constants import TILE_HEIGHT, TILE_WIDTH
from ..inputs.tuning import setting_key, tune
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
    """Something that lives in a level: it sleeps until Mario comes close.

    The class is complete on its own: an entity of ``res/entities.yaml`` whose
    ``behaviour`` is ``generic`` picks its effects with its ``settings``, so a
    walking enemy or an item hidden in a block is pure data. A subclass is
    only needed for a real state machine (see :class:`~src.entities.koopa.Koopa`).
    """

    # Animations the class needs in res/entities.yaml, whatever its settings.
    ANIMATIONS: Tuple[str, ...] = ()
    # Setting -> prefix of the methods it can name (see EFFECTS in the docstring).
    EFFECTS: Dict[str, str] = {
        "MOVEMENT": "move_",
        "ON_STOMP": "react_",
        "ON_TOUCH": "react_",
        "ON_KNOCK": "knock_",
        "ON_WAKE": "wake_",
        "COLLECT": "collect_",
    }
    # Animations an effect needs on top of ANIMATIONS.
    EFFECT_ANIMATIONS: Dict[str, Tuple[str, ...]] = {"squash": ("squashed",)}
    NOT_TUNABLE = ("ANIMATIONS", "EFFECTS", "EFFECT_ANIMATIONS")

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

    # How it moves once awake: walk (straight on) or still.
    MOVEMENT = "walk"
    SPEED = 32.0
    # What Mario gets when he lands on it, then when he touches it from the
    # side: hurt, squash, collect or nothing (a subclass adds its own).
    ON_STOMP = "hurt"
    ON_TOUCH = "hurt"
    SQUASHED_DURATION = 0.5
    # What the reward of a collected entity is: grow or life.
    COLLECT = "grow"
    # Hit by a shell or by the block under it: flip (and fall), hop or nothing.
    ON_KNOCK = "flip"
    HOP_SPEED = 180.0
    # Where it looks when Mario wakes it up: face_mario, left or right.
    ON_WAKE = "face_mario"
    # Animation played while it moves, and whether it looks where it walks.
    ANIMATION = "walk"
    TURNS = True

    def __init__(self, kind: EntityType, sprites: SpriteBank, column: int, row: int):
        self.kind = kind
        tune(self, kind.settings, f"entities.yaml: {kind.id}")
        where = f"entities.yaml: {kind.id}"
        # tune() sets the settings of the file on the instance: they are the
        # values the checks below must use, not the defaults of the class.
        overrides = {name: value for name, value in vars(self).items() if name.isupper()}
        self.check_effects(where, overrides)
        self.animations: Dict[str, Animation] = sprites.build(
            kind.image, kind.animations, kind.facing, kind.palette, kind.id
        )
        missing = [name for name in self.required_animations(overrides) if name not in self.animations]
        if missing:
            raise ValueError(f"{where} needs the animation(s) {', '.join(missing)}")
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
        self.squashed = False
        self.squashed_time = 0.0

    # --- Effects named by the settings ------------------------------------

    @classmethod
    def setting(cls, name: str, values: Optional[Mapping[str, Any]] = None) -> Any:
        """The value of a constant, taken from ``values`` when it changes it."""
        return (values or {}).get(name, getattr(cls, name))

    @classmethod
    def effect_names(cls, prefix: str) -> Tuple[str, ...]:
        """The effects the class offers for a setting (``move_`` gives walk...)."""
        names = (name[len(prefix):] for name in dir(cls) if name.startswith(prefix))
        return tuple(sorted(name for name in names if callable(getattr(cls, prefix + name, None))))

    @classmethod
    def check_effects(cls, where: str, values: Optional[Mapping[str, Any]] = None) -> None:
        """ValueError when a setting names an effect the class does not have."""
        for constant, prefix in cls.EFFECTS.items():
            name = cls.setting(constant, values)
            if not callable(getattr(cls, prefix + str(name), None)):
                known = ", ".join(cls.effect_names(prefix))
                raise ValueError(
                    f"{where}: unknown {setting_key(constant)} {name!r} (known: {known})"
                )

    @classmethod
    def required_animations(cls, values: Optional[Mapping[str, Any]] = None) -> Tuple[str, ...]:
        """The animations ``entities.yaml`` must give, for these settings."""
        names = [*cls.ANIMATIONS, cls.setting("ANIMATION", values)]
        for constant in cls.EFFECTS:
            names.extend(cls.EFFECT_ANIMATIONS.get(cls.setting(constant, values), ()))
        return tuple(dict.fromkeys(names))

    def effect(self, constant: str):
        """The method the setting ``constant`` names, ready to be called."""
        return getattr(self, self.EFFECTS[constant] + getattr(self, constant))

    @property
    def rect(self) -> Rect:
        return self.body.rect

    @property
    def alive(self) -> bool:
        """Can still touch Mario or be touched by a shell."""
        return (
            self.active
            and not self.removed
            and not self.knocked
            and not self.squashed
            and self.emerging <= 0
        )

    @property
    def kills_enemies(self) -> bool:
        """True while it knocks the enemies it meets out (a sliding shell)."""
        return False

    def activate(self, level: Level) -> None:
        """Mario comes close: the entity comes to life (see ``onWake``)."""
        if self.hidden:
            return
        self.active = True
        self.effect("ON_WAKE")(level)

    def wake_face_mario(self, level: Level) -> None:
        self.direction = 1 if level.mario.center_x > self.body.center_x else -1

    def wake_left(self, level: Level) -> None:
        self.direction = -1

    def wake_right(self, level: Level) -> None:
        self.direction = 1

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
        """Template method, called every frame: handles being knocked, rising
        out of a block and falling off the level, and calls ``behave`` the rest
        of the time. Subclasses override ``behave``, not this."""
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
        """What the entity does on each frame once it is awake: its ``movement``
        effect, unless it was squashed and is waiting to disappear."""
        if self.squashed:
            self.squashed_time += dt
            self.removed = self.squashed_time >= self.SQUASHED_DURATION
            return
        self.effect("MOVEMENT")(dt, level)

    def move_walk(self, dt: float, level: Level) -> None:
        self.walk(dt, level, self.SPEED)

    def move_still(self, dt: float, level: Level) -> None:
        """Stays where it is, but still falls."""
        self.walk(dt, level, 0.0)

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
        """Mario touches the entity; ``stomp`` when he falls on its head.
        Runs its ``onStomp`` or its ``onTouch`` effect."""
        self.effect("ON_STOMP" if stomp else "ON_TOUCH")(level, stomp)

    def react_hurt(self, level: Level, stomp: bool) -> None:
        level.hurt_mario()

    def react_squash(self, level: Level, stomp: bool) -> None:
        """Flattened: it stops, is shown squashed, then disappears."""
        self.squashed = True
        self.squashed_time = 0.0
        self.body.vx = 0.0
        level.stomped(self)

    def react_collect(self, level: Level, stomp: bool) -> None:
        """Picked up: it gives its ``collect`` reward and disappears."""
        self.removed = True
        self.effect("COLLECT")(level)

    def react_nothing(self, level: Level, stomp: bool) -> None:
        """Mario goes through it."""

    def collect_grow(self, level: Level) -> None:
        level.grow_mario(self.body.center_x, self.body.y)

    def collect_life(self, level: Level) -> None:
        level.add_life(self.body.center_x, self.body.y)

    def knock(self, level: Level, direction: int) -> None:
        """Hit by a shell or by a block bumped under it: runs ``onKnock``."""
        if self.knocked:
            return
        self.effect("ON_KNOCK")(level, direction)

    def knock_flip(self, level: Level, direction: int) -> None:
        """It flips over and falls off the screen."""
        self.knocked = True
        self.body.vx = direction * 50.0
        self.body.vy = -self.KNOCK_SPEED
        level.score(self.KNOCK_POINTS, self.body.center_x, self.body.y)
        level.play_sound("kick")

    def knock_hop(self, level: Level, direction: int) -> None:
        """It jumps in place, like an item on a bumped block."""
        self.body.vy = -self.HOP_SPEED
        self.body.on_ground = False

    def knock_nothing(self, level: Level, direction: int) -> None:
        """Nothing can knock it out."""

    def image(self) -> Surface:
        """The current picture, taken from ``self.animations``."""
        if self.squashed:
            return self.animations["squashed"].image()
        animation = self.animations[self.ANIMATION]
        # A mirrored animation flips itself; a sprite that does not turn is
        # always drawn as in the sheet.
        facing = self.direction if self.TURNS and not animation.mirror else None
        return animation.image(self.time, facing)

    def draw(self, surface: Surface, camera_x: float, camera_y: float) -> None:
        """Draws ``image()`` with its feet on the body (upside down when knocked)."""
        image = self.image()
        if self.knocked:
            image = transform.flip(image, False, True)
        x = self.body.center_x - image.get_width() / 2 - camera_x
        y = self.body.bottom - image.get_height() - camera_y
        surface.blit(image, (round(x), round(y)))
