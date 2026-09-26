"""Camera view helper converting between map cells and screen coordinates."""

import math
from typing import Optional, Tuple

import pygame

from ..constantes import MAX_ZOOM, MIN_ZOOM, TILE_SIZE

Cell = Tuple[int, int]


class Camera:
    """Visible part of the map. ``x``/``y`` are in map pixels, the zoom is an
    integer so that every sheet pixel is drawn as a square of screen pixels."""

    def __init__(self, columns: int, rows: int, zoom: int = 2) -> None:
        self.columns = columns
        self.rows = rows
        self.zoom = zoom
        self.x = 0.0
        self.y = 0.0
        self.viewport = pygame.Rect(0, 0, 1, 1)

    @property
    def tile_size(self) -> int:
        return TILE_SIZE * self.zoom

    @property
    def view_width(self) -> float:
        return self.viewport.width / self.zoom

    @property
    def view_height(self) -> float:
        return self.viewport.height / self.zoom

    def set_viewport(self, rect: pygame.Rect) -> None:
        """Updates the screen rectangle used for map drawing and clamps position."""
        self.viewport = pygame.Rect(rect)
        self.clamp()

    def set_map_size(self, columns: int, rows: int) -> None:
        """Updates the map dimensions used to keep the camera inside bounds."""
        self.columns = columns
        self.rows = rows
        self.clamp()

    def fit(self) -> None:
        """Zooms so that the whole map height is visible, and goes to the start."""
        zoom = self.viewport.height // max(self.rows * TILE_SIZE, 1)
        self.zoom = min(max(zoom, MIN_ZOOM), MAX_ZOOM)
        self.x = self.y = 0.0
        self.clamp()

    def clamp(self) -> None:
        """Keeps the camera inside the map or centered when the map is smaller."""
        self.x = self._clamp_axis(self.x, self.columns * TILE_SIZE, self.view_width)
        self.y = self._clamp_axis(self.y, self.rows * TILE_SIZE, self.view_height)

    def move(self, dx: float, dy: float) -> None:
        self.x += dx
        self.y += dy
        self.clamp()

    def set_zoom(self, zoom: int, anchor: Optional[Tuple[int, int]] = None) -> bool:
        """Changes the zoom while keeping the map point under ``anchor`` in place."""
        zoom = min(max(zoom, MIN_ZOOM), MAX_ZOOM)
        if zoom == self.zoom:
            return False
        anchor = anchor or self.viewport.center
        world_x, world_y = self.screen_to_world(anchor)
        self.zoom = zoom
        self.x = world_x - (anchor[0] - self.viewport.x) / zoom
        self.y = world_y - (anchor[1] - self.viewport.y) / zoom
        self.clamp()
        return True

    def screen_to_world(self, position: Tuple[int, int]) -> Tuple[float, float]:
        """Converts a screen pixel to an unzoomed map pixel position."""
        return (
            self.x + (position[0] - self.viewport.x) / self.zoom,
            self.y + (position[1] - self.viewport.y) / self.zoom,
        )

    def screen_to_cell(self, position: Tuple[int, int]) -> Cell:
        """Converts a screen pixel to the map cell under it."""
        world_x, world_y = self.screen_to_world(position)
        return math.floor(world_x / TILE_SIZE), math.floor(world_y / TILE_SIZE)

    def cell_to_screen(self, cell: Cell) -> Tuple[int, int]:
        """Converts a map cell to its top-left screen pixel."""
        return (
            self.viewport.x + round((cell[0] * TILE_SIZE - self.x) * self.zoom),
            self.viewport.y + round((cell[1] * TILE_SIZE - self.y) * self.zoom),
        )

    def map_rect(self) -> pygame.Rect:
        """The whole map, in screen coordinates."""
        return pygame.Rect(
            self.cell_to_screen((0, 0)),
            (self.columns * self.tile_size, self.rows * self.tile_size),
        )

    def visible_cells(self) -> Tuple[range, range]:
        """Column and row ranges that intersect the viewport."""
        first_col = max(math.floor(self.x / TILE_SIZE), 0)
        first_row = max(math.floor(self.y / TILE_SIZE), 0)
        last_col = min(math.ceil((self.x + self.view_width) / TILE_SIZE), self.columns)
        last_row = min(math.ceil((self.y + self.view_height) / TILE_SIZE), self.rows)
        return range(first_col, last_col), range(first_row, last_row)

    @staticmethod
    def _clamp_axis(position: float, map_length: float, view_length: float) -> float:
        if map_length <= view_length:
            # The map is smaller than the view: center it.
            return (map_length - view_length) / 2
        return min(max(position, 0.0), map_length - view_length)
