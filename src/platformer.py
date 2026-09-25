"""Movement and collisions of Mario in a platform level.

Positions are in pixels, speeds in pixels per second. The level is a grid of
16x16 cells and ``is_solid(column, row)`` tells which ones block Mario.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, List, Tuple

from pygame import Rect

from .constants import TILE_HEIGHT, TILE_WIDTH

Cell = Tuple[int, int]
IsSolid = Callable[[int, int], bool]


@dataclass
class Controls:
    """What the player holds this frame. ``jump_pressed`` is only true on the
    frame the jump key goes down."""

    left: bool = False
    right: bool = False
    run: bool = False
    jump: bool = False
    jump_pressed: bool = False


class Body:
    WIDTH = 12
    HEIGHT = 15

    WALK_SPEED = 90.0
    RUN_SPEED = 150.0
    ACCELERATION = 300.0
    SKID_DECELERATION = 700.0
    FRICTION = 350.0
    JUMP_SPEED = 250.0
    # Running jumps go higher, like in SMB3.
    JUMP_SPEED_BONUS = 0.25
    GRAVITY = 1300.0
    # Lighter gravity while rising with the jump key held: the longer it is
    # held, the higher the jump.
    JUMP_GRAVITY = 450.0
    MAX_FALL_SPEED = 300.0
    COYOTE_TIME = 0.08
    JUMP_BUFFER = 0.1
    MAX_STEP = 4.0

    def __init__(self, x: float, y: float):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.facing = 1
        self.skidding = False
        self._air_time = 0.0
        self._jump_buffer = 0.0

    @property
    def rect(self) -> Rect:
        return Rect(math.floor(self.x), math.floor(self.y), self.WIDTH, self.HEIGHT)

    @property
    def jumping(self) -> bool:
        return not self.on_ground

    def update(self, dt: float, controls: Controls, is_solid: IsSolid) -> List[Cell]:
        """Moves the body; returns the solid cells its head bumped into."""
        self._walk(dt, controls)
        self._jump(dt, controls)

        dx, dy = self.vx * dt, self.vy * dt
        steps = max(1, math.ceil(max(abs(dx), abs(dy)) / self.MAX_STEP))
        bumped: List[Cell] = []
        was_on_ground, self.on_ground = self.on_ground, False
        for _ in range(steps):
            self._move_x(dx / steps, is_solid)
            bumped += self._move_y(dy / steps, is_solid)
        if self.on_ground:
            self._air_time = 0.0
        elif was_on_ground or self._air_time > 0:
            self._air_time += dt
        return bumped

    def _walk(self, dt: float, controls: Controls) -> None:
        direction = int(controls.right) - int(controls.left)
        max_speed = self.RUN_SPEED if controls.run else self.WALK_SPEED
        self.skidding = bool(direction) and self.vx * direction < 0 and self.on_ground
        if direction:
            self.facing = direction
            if self.vx * direction < 0:
                self.vx += direction * self.SKID_DECELERATION * dt
            elif abs(self.vx) < max_speed:
                self.vx = direction * min(abs(self.vx) + self.ACCELERATION * dt, max_speed)
            else:
                self.vx = direction * max(abs(self.vx) - self.FRICTION * dt, max_speed)
        else:
            speed = max(abs(self.vx) - self.FRICTION * dt, 0.0)
            self.vx = math.copysign(speed, self.vx)

    def _jump(self, dt: float, controls: Controls) -> None:
        if controls.jump_pressed:
            self._jump_buffer = self.JUMP_BUFFER
        can_jump = self.on_ground or 0 < self._air_time <= self.COYOTE_TIME
        if self._jump_buffer > 0 and can_jump and self.vy >= 0:
            self.vy = -(self.JUMP_SPEED + abs(self.vx) * self.JUMP_SPEED_BONUS)
            self._jump_buffer = 0.0
            self._air_time = self.COYOTE_TIME + 1
            self.on_ground = False
        self._jump_buffer = max(0.0, self._jump_buffer - dt)
        gravity = self.JUMP_GRAVITY if self.vy < 0 and controls.jump else self.GRAVITY
        self.vy = min(self.vy + gravity * dt, self.MAX_FALL_SPEED)

    def _columns(self) -> range:
        return range(math.floor(self.x / TILE_WIDTH), math.floor((self.x + self.WIDTH - 1e-6) / TILE_WIDTH) + 1)

    def _rows(self) -> range:
        return range(math.floor(self.y / TILE_HEIGHT), math.floor((self.y + self.HEIGHT - 1e-6) / TILE_HEIGHT) + 1)

    def _move_x(self, dx: float, is_solid: IsSolid) -> None:
        if not dx:
            return
        self.x += dx
        if dx > 0:
            column = math.floor((self.x + self.WIDTH - 1e-6) / TILE_WIDTH)
            if any(is_solid(column, row) for row in self._rows()):
                self.x = column * TILE_WIDTH - self.WIDTH
                self.vx = 0.0
        else:
            column = math.floor(self.x / TILE_WIDTH)
            if any(is_solid(column, row) for row in self._rows()):
                self.x = (column + 1) * TILE_WIDTH
                self.vx = 0.0

    def _move_y(self, dy: float, is_solid: IsSolid) -> List[Cell]:
        if not dy:
            return []
        self.y += dy
        if dy > 0:
            row = math.floor((self.y + self.HEIGHT - 1e-6) / TILE_HEIGHT)
            if any(is_solid(column, row) for column in self._columns()):
                self.y = row * TILE_HEIGHT - self.HEIGHT
                self.vy = 0.0
                self.on_ground = True
            return []
        row = math.floor(self.y / TILE_HEIGHT)
        hit = [(column, row) for column in self._columns() if is_solid(column, row)]
        if not hit:
            return []
        self.y = (row + 1) * TILE_HEIGHT
        self.vy = 0.0
        # Only the block above the middle of Mario is bumped, as in the NES games.
        center = math.floor((self.x + self.WIDTH / 2) / TILE_WIDTH)
        return [min(hit, key=lambda cell: abs(cell[0] - center))]
