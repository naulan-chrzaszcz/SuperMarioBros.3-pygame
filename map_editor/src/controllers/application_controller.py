from typing import Callable

import pygame

from ..constantes import TILE_SIZE
from ..views.application_view import COMMANDS_PANEL, MAP_PANEL, TILES_PANEL

MOUSE_EVENTS = (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION)


class ApplicationController:
    """Routes window events to the panel under the mouse cursor."""

    def __init__(
        self,
        view,
        map_controller,
        commands,
        tile_selection,
        on_save: Callable[[], None],
    ) -> None:
        self.view = view
        self.map_controller = map_controller
        self.commands = commands
        self.tile_selection = tile_selection
        self.on_save = on_save
        self.running = True
        self.update_frame_limits()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type in (pygame.QUIT, pygame.WINDOWCLOSE):
            self.running = False
        elif event.type in MOUSE_EVENTS:
            self._handle_mouse_event(event)
        elif event.type == pygame.MOUSEWHEEL:
            self.tile_selection.handle_event(event)
            self.update_frame_limits()
        elif event.type == pygame.KEYDOWN:
            self._handle_key(event)

    def update_frame_limits(self) -> None:
        sheet = self.tile_selection.sheet_image
        self.commands.set_frame_limits(
            sheet.get_width() // TILE_SIZE - self.tile_selection.selection_x,
            sheet.get_height() // TILE_SIZE - self.tile_selection.selection_y,
        )

    def _handle_mouse_event(self, event: pygame.event.Event) -> None:
        panel = self.view.panel_at(event.pos)
        if panel is None:
            return

        attributes = dict(event.dict)
        attributes["pos"] = self.view.to_local(panel, event.pos)
        local_event = pygame.event.Event(event.type, attributes)

        if panel == MAP_PANEL:
            self.map_controller.handle_event(local_event)
        elif panel == COMMANDS_PANEL:
            self.commands.handle_event(local_event)
        elif panel == TILES_PANEL:
            self.tile_selection.handle_event(local_event)
            self.update_frame_limits()

    def _handle_key(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_ESCAPE:
            self.running = False
        elif event.key == pygame.K_s and event.mod & pygame.KMOD_CTRL:
            self.on_save()
        elif event.key == pygame.K_r:
            self.commands.rotate()
        else:
            self.map_controller.handle_event(event)
