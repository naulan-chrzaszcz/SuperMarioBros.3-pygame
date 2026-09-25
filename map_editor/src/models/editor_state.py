from dataclasses import dataclass
from enum import Enum
from typing import Optional

from ..constantes import MESSAGE_DURATION
from ..outputs.tile import Tile
from .tileset import Tileset


class Mode(Enum):
    TILES = "Tiles"
    COLLISIONS = "Collisions"


class MessageLevel(Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class EditorState:
    """Current tool settings: the single source of truth shared by every view."""

    tileset: Tileset
    selection_x: int = 0
    selection_y: int = 0
    rotation: int = 0
    frames_x: int = 1
    frames_y: int = 1
    mode: Mode = Mode.TILES
    show_grid: bool = True
    show_collisions: bool = True
    message: str = ""
    message_level: MessageLevel = MessageLevel.INFO
    message_timer: float = 0.0

    def __post_init__(self) -> None:
        if not self.tileset.is_declared(self.selection_x, self.selection_y):
            first = next(self.tileset.declared_cells(), None)
            if first is not None:
                self.selection_x, self.selection_y = first
        self.select(self.selection_x, self.selection_y)

    @property
    def max_frames_x(self) -> int:
        return self.tileset.columns - self.selection_x

    @property
    def max_frames_y(self) -> int:
        return self.tileset.rows - self.selection_y

    @property
    def selected_name(self) -> Optional[str]:
        return self.tileset.name_of(self.selection_x, self.selection_y)

    @property
    def selection_declared(self) -> bool:
        return self.tileset.is_declared(self.selection_x, self.selection_y)

    def selected_tile(self) -> Tile:
        return Tile(
            self.selection_x,
            self.selection_y,
            self.frames_x,
            self.frames_y,
            self.rotation,
        )

    def select(self, x: int, y: int) -> None:
        self.selection_x = min(max(x, 0), self.tileset.columns - 1)
        self.selection_y = min(max(y, 0), self.tileset.rows - 1)
        self.frames_x = min(self.frames_x, self.max_frames_x)
        self.frames_y = min(self.frames_y, self.max_frames_y)

    def cycle_selection(self, step: int) -> None:
        """Moves the selection to the next/previous usable tile of the sheet."""
        cells = list(self.tileset.declared_cells())
        if not cells:
            return
        current = (self.selection_x, self.selection_y)
        index = cells.index(current) if current in cells else -1
        self.select(*cells[(index + step) % len(cells)])

    def rotate(self, direction: int = 1) -> None:
        self.rotation = (self.rotation + 90 * direction) % 360

    def set_frames_x(self, value: int) -> None:
        self.frames_x = min(max(value, 1), self.max_frames_x)
        if self.frames_x > 1:
            self.frames_y = 1

    def set_frames_y(self, value: int) -> None:
        self.frames_y = min(max(value, 1), self.max_frames_y)
        if self.frames_y > 1:
            self.frames_x = 1

    def pick(self, tile: Tile) -> None:
        self.frames_x = self.frames_y = 1
        self.select(tile.x, tile.y)
        self.rotation = tile.rotation
        self.set_frames_x(tile.x_frames)
        self.set_frames_y(tile.y_frames)
        self.mode = Mode.TILES

    def toggle_mode(self) -> None:
        self.mode = Mode.COLLISIONS if self.mode is Mode.TILES else Mode.TILES

    def notify(
        self,
        message: str,
        level: MessageLevel = MessageLevel.INFO,
        duration: float = MESSAGE_DURATION,
    ) -> None:
        self.message = message
        self.message_level = level
        self.message_timer = duration

    def update(self, dt: float) -> None:
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = ""
