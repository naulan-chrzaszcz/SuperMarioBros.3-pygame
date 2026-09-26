"""The ``koopa`` behaviour of ``res/entities.yaml`` (also used by ``red_koopa``):
walks, hides in its shell when stomped, and the shell can be kicked.

Only the shell state machine needs Python: the rest of the koopa (how it walks,
what touching it does) is chosen by the settings of the file, like every entity.
"""

from __future__ import annotations

from enum import Enum, auto

from pygame import Surface

from .entity import Entity, Level


class Shell(Enum):
    NONE = auto()  # walking
    STILL = auto()
    SLIDING = auto()


class Koopa(Entity):
    """A Koopa Troopa: walks off ledges like a goomba (a red one, with
    ``turnAtLedges``, turns back instead).

    Stomping it makes it hide in its shell. Touching the still shell kicks it:
    the shell slides, bounces off walls and knocks out every enemy on its way,
    but hurts Mario when he runs into it. A stomp stops it. A still shell wakes
    up after a while.

    It adds the ``shell`` effect, which ``onStomp`` and ``onTouch`` name in
    ``entities.yaml``, and the ``koopa`` movement, which drives its shell.
    """

    ANIMATIONS = ("walk", "shell", "spin", "shake")
    ENEMY = True
    HEIGHT = 24
    SHELL_HEIGHT = 14
    MOVEMENT = "koopa"
    ON_STOMP = "shell"
    ON_TOUCH = "shell"
    SPEED = 32.0
    SHELL_SPEED = 180.0
    WAKE_UP_TIME = 7.0
    SHAKE_TIME = 1.5  # the shell shakes before the koopa comes out
    # Right after a kick, the shell cannot hurt the Mario who kicked it.
    KICK_GRACE = 0.25
    KICK_POINTS = 100

    def __init__(self, *args):
        super().__init__(*args)
        self.shell = Shell.NONE
        self.shell_time = 0.0

    @property
    def kills_enemies(self) -> bool:
        return self.alive and self.shell is Shell.SLIDING

    def move_koopa(self, dt: float, level: Level) -> None:
        """Walks, slides as a shell, or waits in the shell until it wakes up."""
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
                self.wake_face_mario(level)

    def walk(self, dt: float, level: Level, speed: float) -> None:
        # A sliding shell falls from the ledges, even the one of a red koopa.
        turn_at_ledges = self.TURN_AT_LEDGES
        self.TURN_AT_LEDGES = turn_at_ledges and self.shell is Shell.NONE
        super().walk(dt, level, speed)
        self.TURN_AT_LEDGES = turn_at_ledges

    def react_shell(self, level: Level, stomp: bool) -> None:
        """Kicks the still shell, hides in it when stomped, hurts Mario else."""
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
            self.react_hurt(level, stomp)

    def kick(self, level: Level, direction: int, score: bool = True) -> None:
        self._set_shell(Shell.SLIDING)
        self.direction = direction
        self.ignore_mario = self.KICK_GRACE
        level.play_sound("kick")
        if score:
            level.score(self.KICK_POINTS, self.body.center_x, self.body.y)

    def knock_flip(self, level: Level, direction: int) -> None:
        if self.shell is Shell.NONE:
            self.body.resize(self.SHELL_HEIGHT)
        super().knock_flip(level, direction)

    def _set_shell(self, shell: Shell) -> None:
        self.shell = shell
        self.shell_time = 0.0
        self.body.vx = 0.0

    def image(self) -> Surface:
        if self.shell is Shell.NONE and not self.knocked:
            return super().image()
        if self.shell is Shell.SLIDING:
            return self.animations["spin"].image(self.time)
        if self.shell is Shell.STILL and self.shell_time >= self.WAKE_UP_TIME - self.SHAKE_TIME:
            return self.animations["shake"].image(self.time)
        return self.animations["shell"].image()
