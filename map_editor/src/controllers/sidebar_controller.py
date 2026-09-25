import pygame

from ..models import EditorState, MessageLevel
from ..views.sidebar_view import SidebarView


class SidebarController:
    """Clicks on the tool buttons and on the tileset picker."""

    def __init__(self, state: EditorState, view: SidebarView) -> None:
        self.state = state
        self.view = view

    def handle_mouse(self, event: pygame.event.Event) -> None:
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        for button in self.view.buttons:
            if button.click(event.pos):
                return
        cell = self.view.tileset_cell_at(event.pos)
        if cell is not None:
            self.state.select(*cell)
            if not self.state.selection_declared:
                self.state.notify(
                    f"Tile {cell[0]},{cell[1]} is {self.state.tileset.missing_reason}",
                    MessageLevel.WARNING,
                )

    def handle_wheel(self, event: pygame.event.Event, mouse) -> None:
        if self.view.tileset_rect.collidepoint(mouse) and event.y:
            self.state.cycle_selection(-1 if event.y > 0 else 1)
