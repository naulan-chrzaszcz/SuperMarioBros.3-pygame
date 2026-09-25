from __future__ import annotations

from enum import Enum, auto

from pygame import Surface

from .entity import Entity, Level, Sprites


class Shell(Enum):
    NONE = auto()  # walking
    STILL = auto()
    SLIDING = auto()


class Koopa(Entity):
    """A green Koopa Troopa: walks off ledges like a goomba.

    Stomping it makes it hide in its shell. Touching the still shell kicks it:
    the shell slides, bounces off walls and knocks out every enemy on its way,
    but hurts Mario when he runs into it. A stomp stops it. A still shell wakes
    up after a while.
    """

    TYPE = "koopa"
    ENEMY = True
    HEIGHT = 24
    SHELL_HEIGHT = 14
    SPEED = 32.0
    SHELL_SPEED = 180.0
    STEP_DURATION = 0.15
    SPIN_DURATION = 0.05
    WAKE_UP_TIME = 7.0
    SHAKE_TIME = 1.5  # the shell shakes before the koopa comes out
    # Right after a kick, the shell cannot hurt the Mario who kicked it.
    KICK_GRACE = 0.25
    KICK_POINTS = 100

    def __init__(self, sprites: Sprites, column: int, row: int):
        super().__init__(sprites, column, row)
        self.walking = [sprites.frame("koopa", (x, 0, 16, 27)) for x in (0, 16)]
        # The last shell of the sheet is one pixel narrower.
        self.shells = [
            sprites.frame("koopa", (x, 0, 16 if x < 96 else 15, 16))[-1] for x in (32, 48, 64, 80, 96)
        ]
        self.shell = Shell.NONE
        self.shell_time = 0.0

    @property
    def kills_enemies(self) -> bool:
        return self.alive and self.shell is Shell.SLIDING

    def update(self, dt: float, level: Level) -> None:
        super().update(dt, level)
        if self.knocked:
            return
        self.shell_time += dt
        if self.shell is Shell.NONE:
            self.walk(dt, level, self.SPEED)
        elif self.shell is Shell.SLIDING:
            self.walk(dt, level, self.SHELL_SPEED)
        else:
            self.walk(dt, level, 0.0)
            if self.shell_time >= self.WAKE_UP_TIME:
                self._set_shell(Shell.NONE)
                self.body.resize(self.HEIGHT)
                self.direction = 1 if level.mario.center_x > self.body.center_x else -1

    def touch_mario(self, level: Level, stomp: bool) -> None:
        if self.shell is Shell.STILL:
            direction = 1 if self.body.center_x >= level.mario.center_x else -1
            self.kick(level, direction, score=not stomp)
            if stomp:
                level.stomped(self)
        elif stomp:
            self._set_shell(Shell.STILL)
            self.body.resize(self.SHELL_HEIGHT)
            level.stomped(self)
        else:
            level.hurt_mario()

    def kick(self, level: Level, direction: int, score: bool = True) -> None:
        self._set_shell(Shell.SLIDING)
        self.direction = direction
        self.ignore_mario = self.KICK_GRACE
        if score:
            level.score(self.KICK_POINTS, self.body.center_x, self.body.y)

    def knock(self, level: Level, direction: int) -> None:
        if self.shell is Shell.NONE:
            self.body.resize(self.SHELL_HEIGHT)
        super().knock(level, direction)

    def _set_shell(self, shell: Shell) -> None:
        self.shell = shell
        self.shell_time = 0.0
        self.body.vx = 0.0

    def image(self) -> Surface:
        if self.shell is Shell.NONE and not self.knocked:
            step = int(self.time / self.STEP_DURATION) % 2
            return self.walking[step][self.direction]
        if self.shell is Shell.SLIDING:
            return self.shells[(0, 2, 3, 4)[int(self.time / self.SPIN_DURATION) % 4]]
        if self.shell is Shell.STILL and self.shell_time >= self.WAKE_UP_TIME - self.SHAKE_TIME:
            return self.shells[int(self.time / self.STEP_DURATION) % 2]
        return self.shells[0]
