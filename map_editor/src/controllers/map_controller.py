from typing import Iterator, Optional

import pygame

from ..constantes import SCROLL_TILES, TILE_SIZE
from ..models import EditorState, MapEditorModel, MessageLevel, Mode
from ..views.camera import Camera, Cell
from ..views.map_view import RectangleSelection

PICK_MAX_DISTANCE = 4


class MapController:
    """Mouse and keyboard interactions on the map area."""

    def __init__(self, model: MapEditorModel, state: EditorState, camera: Camera) -> None:
        self.model = model
        self.state = state
        self.camera = camera
        self.hover_cell: Optional[Cell] = None
        self._stroke_button: Optional[int] = None
        self._last_cell: Optional[Cell] = None
        self._rectangle: Optional[RectangleSelection] = None
        self._panning = False
        self._pan_distance = 0

    @property
    def is_dragging(self) -> bool:
        return self._stroke_button is not None or self._rectangle is not None or self._panning

    @property
    def rectangle(self) -> Optional[RectangleSelection]:
        return self._rectangle

    def handle_mouse(self, event: pygame.event.Event) -> None:
        cell = self.camera.screen_to_cell(event.pos)
        if event.type == pygame.MOUSEMOTION:
            self._on_motion(event, cell)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._on_press(event, cell)
        elif event.type == pygame.MOUSEBUTTONUP:
            self._on_release(event, cell)

    def handle_wheel(self, event: pygame.event.Event, mouse) -> None:
        mods = pygame.key.get_mods()
        step = SCROLL_TILES * TILE_SIZE
        if mods & pygame.KMOD_CTRL:
            self.camera.set_zoom(self.camera.zoom + (1 if event.y > 0 else -1), mouse)
        elif mods & pygame.KMOD_SHIFT:
            self.camera.move(-event.y * step, 0)
        else:
            self.camera.move(event.x * step, -event.y * step)
        self.hover_cell = self.camera.screen_to_cell(mouse)

    def handle_key(self, event: pygame.event.Event) -> bool:
        directions = {
            pygame.K_LEFT: (-1, 0),
            pygame.K_RIGHT: (1, 0),
            pygame.K_UP: (0, -1),
            pygame.K_DOWN: (0, 1),
        }
        if event.key not in directions:
            return False
        dx, dy = directions[event.key]
        if event.mod & pygame.KMOD_SHIFT:
            self.camera.move(dx * self.camera.view_width, dy * self.camera.view_height)
        else:
            self.camera.move(dx * TILE_SIZE, dy * TILE_SIZE)
        return True

    def leave(self) -> None:
        if not self.is_dragging:
            self.hover_cell = None

    def _on_motion(self, event, cell: Cell) -> None:
        if self._panning:
            dx, dy = event.rel
            self._pan_distance += abs(dx) + abs(dy)
            self.camera.move(-dx / self.camera.zoom, -dy / self.camera.zoom)
            cell = self.camera.screen_to_cell(event.pos)
        if self._stroke_button is not None:
            for crossed in self._line(self._last_cell, cell):
                self._apply(crossed, self._stroke_button)
            self._last_cell = cell
        if self._rectangle is not None:
            self._rectangle = (self._rectangle[0], cell, self._rectangle[2])
        self.hover_cell = cell

    def _on_press(self, event, cell: Cell) -> None:
        self.hover_cell = cell
        if self.is_dragging:
            return
        if event.button == 2:
            self._panning = True
            self._pan_distance = 0
        elif event.button in (1, 3):
            if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                self._rectangle = (cell, cell, event.button)
            else:
                self.model.begin_edit()
                self._stroke_button = event.button
                self._last_cell = cell
                self._apply(cell, event.button)

    def _on_release(self, event, cell: Cell) -> None:
        if event.button == 2 and self._panning:
            self._panning = False
            if self._pan_distance <= PICK_MAX_DISTANCE:
                self.pick(cell)
        elif event.button == self._stroke_button:
            self._stroke_button = None
            self.model.end_edit()
        elif self._rectangle is not None and event.button == self._rectangle[2]:
            start, _, button = self._rectangle
            self._rectangle = None
            with self.model.edit():
                for rectangle_cell in self.model.cells_between(start, cell):
                    self._apply(rectangle_cell, button)

    def pick(self, cell: Cell) -> None:
        """Eyedropper: selects the tile (and its settings) found in ``cell``."""
        tile = self.model.tiles.get(cell)
        if tile is None:
            return
        self.state.pick(tile)
        name = self.state.selected_name or f"{tile.x},{tile.y}"
        self.state.notify(f"Picked {name}")

    def _apply(self, cell: Cell, button: int) -> None:
        if not self.model.contains(cell):
            return
        if self.state.mode is Mode.COLLISIONS:
            self.model.set_collidable(cell, button == 1)
        elif button != 1:
            self.model.set_tile(cell, None)
        elif self.state.selection_declared:
            self.model.set_tile(cell, self.state.selected_tile())
        else:
            metadata = self.state.tileset.metadata_path.name
            self.state.notify(
                f"This tile is not declared in {metadata}: the game could not load it",
                MessageLevel.WARNING,
            )

    @staticmethod
    def _line(start: Optional[Cell], end: Cell) -> Iterator[Cell]:
        """Cells crossed between two mouse positions (Bresenham), so that fast
        mouse movements do not leave holes."""
        if start is None:
            yield end
            return
        x, y = start
        dx, dy = abs(end[0] - x), -abs(end[1] - y)
        sx = 1 if end[0] > x else -1
        sy = 1 if end[1] > y else -1
        error = dx + dy
        while True:
            yield x, y
            if (x, y) == end:
                return
            doubled = 2 * error
            if doubled >= dy:
                error += dy
                x += sx
            if doubled <= dx:
                error += dx
                y += sy
