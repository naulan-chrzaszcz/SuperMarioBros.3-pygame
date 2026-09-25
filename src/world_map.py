from __future__ import annotations

import re
from typing import Callable, Dict, Optional, Tuple

from pygame import Vector2

from .constants import TILE_HEIGHT, TILE_WIDTH
from .inputs.config import Action

Cell = Tuple[int, int]

DIRECTIONS: Dict[Action, Cell] = {
    Action.UP: (0, -1),
    Action.DOWN: (0, 1),
    Action.LEFT: (-1, 0),
    Action.RIGHT: (1, 0),
}

LEVEL_TILE = re.compile(r"level_?(\d+)")


def level_scene_of(tile_name: str) -> Optional[str]:
    """Scene entered from a world map tile: ``level1`` gives ``level_1``."""
    match = LEVEL_TILE.fullmatch(tile_name or "")
    return f"level_{int(match.group(1))}" if match else None


class WorldMapWalker:
    """Moves the player one cell at a time on the world map grid.

    A move is refused before it starts when the destination is blocked, so the
    player never enters a wall and bounces back.
    """

    def __init__(self, cell: Cell, is_blocked: Callable[[int, int], bool], step_duration: float = 0.1):
        self.cell = cell
        self.target = cell
        self.progress = 1.0
        self.is_blocked = is_blocked
        self.step_duration = step_duration

    @property
    def moving(self) -> bool:
        return self.target != self.cell

    def try_move(self, direction: Action) -> bool:
        if self.moving or direction not in DIRECTIONS:
            return False
        dx, dy = DIRECTIONS[direction]
        destination = (self.cell[0] + dx, self.cell[1] + dy)
        if self.is_blocked(*destination):
            return False
        self.target = destination
        self.progress = 0.0
        return True

    def update(self, dt: float) -> None:
        if not self.moving:
            return
        self.progress = min(1.0, self.progress + dt / self.step_duration)
        if self.progress >= 1.0:
            self.cell = self.target

    @property
    def position(self) -> Vector2:
        """Top left corner of the player, in map pixels."""
        start = Vector2(self.cell[0] * TILE_WIDTH, self.cell[1] * TILE_HEIGHT)
        end = Vector2(self.target[0] * TILE_WIDTH, self.target[1] * TILE_HEIGHT)
        return start.lerp(end, self.progress if self.moving else 1.0)
