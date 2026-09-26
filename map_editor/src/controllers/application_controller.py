"""Application-level controller for global shortcuts, saving and quitting."""

from __future__ import annotations

from pathlib import Path

import pygame

from ..constants import QUIT_CONFIRMATION_DELAY
from ..models import EditorState, MapEditorModel, MessageLevel
from ..views import ApplicationView, Camera
from .map_controller import MapController
from .sidebar_controller import SidebarController

MOUSE_EVENTS = (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION)


class ApplicationController:
    """Global shortcuts, saving, quitting and routing of the mouse events to the
    area under the cursor."""

    def __init__(
        self,
        map_path: Path,
        model: MapEditorModel,
        state: EditorState,
        camera: Camera,
        view: ApplicationView,
        map_controller: MapController,
        sidebar_controller: SidebarController,
    ) -> None:
        self.map_path = Path(map_path)
        self.model = model
        self.state = state
        self.camera = camera
        self.view = view
        self.map_controller = map_controller
        self.sidebar_controller = sidebar_controller
        self.running = True
        # True when the window was closed, False when the user only left the
        # editor with Esc (the launcher is then shown again).
        self.window_closed = False
        # Testing the map needs the game: only possible when the editor is
        # opened from it. play_requested tells the game to start the map.
        self.can_play = False
        self.play_requested = False
        self._quit_deadline = 0.0
        self.time = 0.0

    def update(self, dt: float) -> None:
        self.time += dt

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.request_quit(window=True)
        elif event.type == pygame.VIDEORESIZE:
            self.view.layout(self.view.screen.get_size())
        elif event.type == pygame.WINDOWLEAVE:
            self.map_controller.leave()
        elif event.type in MOUSE_EVENTS:
            self._route_mouse(event)
        elif event.type == pygame.MOUSEWHEEL:
            mouse = pygame.mouse.get_pos()
            if self.view.map_rect.collidepoint(mouse):
                self.map_controller.handle_wheel(event, mouse)
            else:
                self.sidebar_controller.handle_wheel(event, mouse)
        elif event.type == pygame.KEYDOWN:
            self._handle_key(event)

    def save(self) -> bool:
        try:
            self.model.save(self.map_path, self.state.tileset.sheet_path)
        except (OSError, ValueError) as error:
            self.state.notify(f"Save failed: {error}", MessageLevel.ERROR)
            return False
        undeclared = self.model.undeclared_tiles(self.state.tileset)
        if undeclared:
            self.state.notify(
                f"Saved, but {len(undeclared)} tile type(s) are "
                f"{self.state.tileset.missing_reason}: the game will fail to load this map",
                MessageLevel.WARNING,
            )
        else:
            self.state.notify(f"Saved to {self.map_path.name}", MessageLevel.SUCCESS)
        return True

    def request_play(self) -> None:
        """Saves the map and leaves the editor so that the game plays it."""
        if not self.can_play:
            self.state.notify(
                "Open the editor from the game (MAP EDITOR on the title screen) to test the map",
                MessageLevel.WARNING,
            )
            return
        if (self.model.dirty or not self.map_path.exists()) and not self.save():
            return
        if self.model.undeclared_tiles(self.state.tileset):
            self.state.notify(
                f"Cannot play: some tile types are {self.state.tileset.missing_reason}",
                MessageLevel.ERROR,
            )
            return
        self.play_requested = True
        self.running = False

    def resume(self) -> None:
        """Runs the editor again after the game played the map."""
        self.running = True
        self.window_closed = False
        self.play_requested = False
        self._quit_deadline = 0.0

    def undo(self) -> None:
        if not self.model.undo():
            self.state.notify("Nothing to undo")

    def redo(self) -> None:
        if not self.model.redo():
            self.state.notify("Nothing to redo")

    def zoom(self, delta: int) -> None:
        mouse = pygame.mouse.get_pos()
        anchor = mouse if self.view.map_rect.collidepoint(mouse) else None
        self.camera.set_zoom(self.camera.zoom + delta, anchor)

    def request_quit(self, window: bool = False) -> None:
        """Quits, asking for a confirmation first when there are unsaved changes."""
        if not self.model.dirty or self.time < self._quit_deadline:
            self.running = False
            self.window_closed = window
            return
        self._quit_deadline = self.time + QUIT_CONFIRMATION_DELAY
        again = "close the window" if window else "press Esc"
        self.state.notify(
            f"Unsaved changes! {again.capitalize()} again to quit without saving, Ctrl+S to save",
            MessageLevel.WARNING,
            QUIT_CONFIRMATION_DELAY,
        )

    def _route_mouse(self, event: pygame.event.Event) -> None:
        # A drag started on the map keeps going even if the cursor leaves it.
        if self.map_controller.is_dragging or self.view.map_rect.collidepoint(event.pos):
            self.map_controller.handle_mouse(event)
            return
        if event.type == pygame.MOUSEMOTION:
            self.map_controller.leave()
        if self.view.sidebar_rect.collidepoint(event.pos):
            self.sidebar_controller.handle_mouse(event)

    def _handle_key(self, event: pygame.event.Event) -> None:
        ctrl = event.mod & pygame.KMOD_CTRL
        shift = event.mod & pygame.KMOD_SHIFT
        key = event.key
        maps = self.map_controller
        if key == pygame.K_ESCAPE:
            if self.state.pasting:
                self.state.pasting = False
            elif self.state.region is not None:
                self.state.region = None
            else:
                self.request_quit()
        elif key == pygame.K_F5:
            self.request_play()
        elif ctrl and key == pygame.K_s:
            self.save()
        elif ctrl and key == pygame.K_z:
            self.redo() if shift else self.undo()
        elif ctrl and key == pygame.K_y:
            self.redo()
        elif ctrl and key == pygame.K_c:
            maps.copy()
        elif ctrl and key == pygame.K_x:
            maps.cut()
        elif ctrl and key == pygame.K_v:
            maps.start_pasting()
        elif ctrl and key == pygame.K_a:
            maps.select_all()
        elif ctrl:
            return
        elif key in (pygame.K_DELETE, pygame.K_BACKSPACE):
            maps.delete_selection()
        elif key == pygame.K_r and self.state.pasting:
            self.state.rotate_clipboard(-1 if shift else 1)
        elif key == pygame.K_r:
            self.state.rotate(-1 if shift else 1)
        elif key == pygame.K_s:
            self.state.toggle_select_mode()
        elif key == pygame.K_c:
            self.state.toggle_mode()
        elif key == pygame.K_e:
            self.state.toggle_entities_mode()
        elif key == pygame.K_g:
            self.state.show_grid = not self.state.show_grid
        elif key == pygame.K_o:
            self.state.show_collisions = not self.state.show_collisions
        elif key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
            self.zoom(1)
        elif key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            self.zoom(-1)
        elif key == pygame.K_HOME:
            self.camera.fit()
        else:
            self.map_controller.handle_key(event)
