import sys
from pathlib import Path
from typing import Optional, Tuple

import pygame

from .constantes import (
    BACKGROUND_COLOR,
    DEFAULT_MAP_SIZE,
    DEFAULT_WINDOW_SIZE,
    FRAMERATE_LIMIT,
    MIN_WINDOW_SIZE,
)
from .controllers import ApplicationController, MapController, SidebarController
from .models import Clipboard, EditorState, MapEditorModel, MessageLevel, Mode, Tileset
from .views import (
    ApplicationView,
    Button,
    Camera,
    EntityRenderer,
    MapView,
    SidebarView,
    StatusBarView,
    TileRenderer,
)

WINDOW_TITLE = "SuperMarioBros3 - Map editor"


class MapEditorApplication:
    """Builds the models, views and controllers of the editor and runs it."""

    def __init__(
        self,
        map_path: Path,
        sheet_path: Path,
        size: Optional[Tuple[int, int]] = None,
        window_size: Optional[Tuple[int, int]] = None,
        clipboard: Optional[Clipboard] = None,
        playable: bool = False,
    ) -> None:
        self.map_path = Path(map_path)
        self.tileset = Tileset.load(sheet_path)
        # The clipboard is kept when another map is opened from the launcher.
        self.state = EditorState(self.tileset, clipboard=clipboard)

        if self.map_path.is_file():
            self.model = MapEditorModel.from_file(self.map_path)
            if size is not None and size != (self.model.columns, self.model.rows):
                self.model.resize(*size)
                self.state.notify(f"Map resized to {size[0]}x{size[1]} (not saved yet)")
        else:
            self.model = MapEditorModel(*(size or DEFAULT_MAP_SIZE))
            self.state.notify(f"New map: it will be created on save ({self.map_path.name})")

        undeclared = self.model.undeclared_tiles(self.tileset)
        if undeclared:
            self.state.notify(
                f"{len(undeclared)} tile type(s) of this map are {self.tileset.missing_reason}",
                MessageLevel.WARNING,
            )

        self.camera = Camera(self.model.columns, self.model.rows)
        renderer = TileRenderer(self.tileset)
        entity_renderer = EntityRenderer()
        self.map_view = MapView(renderer, entity_renderer)
        self.sidebar_view = SidebarView(self.state, renderer, entity_renderer)
        self.status_bar_view = StatusBarView()
        self.view = ApplicationView(
            self.sidebar_view, self.camera, window_size or self._default_window_size()
        )

        self.map_controller = MapController(self.model, self.state, self.camera)
        self.sidebar_controller = SidebarController(self.state, self.sidebar_view)
        self.controller = ApplicationController(
            self.map_path,
            self.model,
            self.state,
            self.camera,
            self.view,
            self.map_controller,
            self.sidebar_controller,
        )
        self.controller.can_play = playable
        self.sidebar_view.set_rows(self._create_buttons())
        self.camera.fit()

    def run(self) -> None:
        clock = pygame.time.Clock()
        while self.controller.running:
            self.step(pygame.event.get(), clock.tick(FRAMERATE_LIMIT) / 1000.0)
        if self.model.dirty and not self.controller.play_requested:
            print("Warning: the editor closed with unsaved changes", file=sys.stderr)

    def resume(self) -> None:
        """Prepares a new ``run`` after the game played the map."""
        self.view.reopen()
        self.controller.resume()

    def step(self, events, dt: float) -> None:
        for event in events:
            self.controller.handle_event(event)
        self.controller.update(dt)
        self.state.update(dt)
        self.render()

    def render(self) -> None:
        screen = self.view.screen
        time = self.controller.time
        screen.fill(BACKGROUND_COLOR)
        self.map_view.draw(
            screen,
            self.camera,
            self.model,
            self.state,
            self.map_controller.hover_cell,
            self.map_controller.rectangle,
            time,
        )
        self.sidebar_view.draw(screen, self.view.font, pygame.mouse.get_pos(), time)
        self.status_bar_view.draw(
            screen,
            self.view.status_rect,
            self.view.font,
            self.model,
            self.state,
            self.camera,
            self.map_controller.hover_cell,
        )
        dirty = " *" if self.model.dirty else ""
        self.view.set_caption(f"{self.map_path.name}{dirty} - {WINDOW_TITLE}")
        pygame.display.flip()

    def _create_buttons(self):
        state = self.state
        controller = self.controller
        maps = self.map_controller
        return [
            [
                Button("Rotate  (R)", state.rotate),
                Button("Fit view  (Home)", self.camera.fit),
            ],
            [
                Button("-", lambda: state.set_frames_x(state.frames_x - 1)),
                Button(lambda: f"Frames X: {state.frames_x}"),
                Button("+", lambda: state.set_frames_x(state.frames_x + 1)),
            ],
            [
                Button("-", lambda: state.set_frames_y(state.frames_y - 1)),
                Button(lambda: f"Frames Y: {state.frames_y}"),
                Button("+", lambda: state.set_frames_y(state.frames_y + 1)),
            ],
            [
                Button("Tiles", lambda: state.set_mode(Mode.TILES),
                       is_active=lambda: state.mode is Mode.TILES),
                Button("Solid", lambda: state.set_mode(Mode.COLLISIONS),
                       is_active=lambda: state.mode is Mode.COLLISIONS),
                Button("Entities", lambda: state.set_mode(Mode.ENTITIES),
                       is_active=lambda: state.mode is Mode.ENTITIES),
                Button("Select", lambda: state.set_mode(Mode.SELECT),
                       is_active=lambda: state.mode is Mode.SELECT),
            ],
            [
                Button("Copy", maps.copy, is_enabled=lambda: state.region is not None),
                Button("Cut", maps.cut, is_enabled=lambda: state.region is not None),
                Button("Paste", maps.start_pasting,
                       is_active=lambda: state.pasting, is_enabled=lambda: state.can_paste),
                Button("Clear", maps.delete_selection, is_enabled=lambda: state.region is not None),
            ],
            [
                Button("Grid  (G)", lambda: setattr(state, "show_grid", not state.show_grid),
                       is_active=lambda: state.show_grid),
                Button("Solid overlay  (O)",
                       lambda: setattr(state, "show_collisions", not state.show_collisions),
                       is_active=lambda: state.show_collisions),
            ],
            [
                Button("Undo", controller.undo, is_enabled=lambda: self.model.can_undo),
                Button("Redo", controller.redo, is_enabled=lambda: self.model.can_redo),
                Button("Save", controller.save, is_enabled=lambda: self.model.dirty
                       or not self.map_path.exists()),
            ],
            [
                Button("Play the map  (F5)", controller.request_play,
                       is_enabled=lambda: controller.can_play),
            ],
        ]

    @staticmethod
    def _default_window_size() -> Tuple[int, int]:
        desktop_width, desktop_height = pygame.display.get_desktop_sizes()[0]
        width = min(DEFAULT_WINDOW_SIZE[0], int(desktop_width * 0.9))
        height = min(DEFAULT_WINDOW_SIZE[1], int(desktop_height * 0.85))
        return max(width, MIN_WINDOW_SIZE[0]), max(height, MIN_WINDOW_SIZE[1])
