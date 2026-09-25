from typing import Optional

import pygame

from ..constantes import (
    BORDER_COLOR,
    ERROR_COLOR,
    INFO_COLOR,
    MUTED_TEXT_COLOR,
    PANEL_COLOR,
    PANEL_PADDING,
    SUCCESS_COLOR,
    TEXT_COLOR,
    WARNING_COLOR,
)
from ..models import EditorState, MapEditorModel, MessageLevel, region_size
from .camera import Camera, Cell

MESSAGE_COLORS = {
    MessageLevel.INFO: INFO_COLOR,
    MessageLevel.SUCCESS: SUCCESS_COLOR,
    MessageLevel.WARNING: WARNING_COLOR,
    MessageLevel.ERROR: ERROR_COLOR,
}
SEPARATOR = "     |     "


class StatusBarView:
    """Hovered cell, map information and the latest editor message."""

    def draw(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        font: pygame.font.Font,
        model: MapEditorModel,
        state: EditorState,
        camera: Camera,
        hover_cell: Optional[Cell],
    ) -> None:
        pygame.draw.rect(surface, PANEL_COLOR, rect)
        pygame.draw.line(surface, BORDER_COLOR, rect.topleft, rect.topright)

        parts = [f"Map {model.columns}x{model.rows}", f"Zoom x{camera.zoom}", f"Mode: {state.mode.value}"]
        if state.pasting:
            parts.append(f"Pasting {state.clipboard.columns}x{state.clipboard.rows}")
        elif state.region is not None:
            parts.append("Selection {}x{}".format(*region_size(state.region)))
        if hover_cell is not None and model.contains(hover_cell):
            parts.insert(0, f"Cell {hover_cell[0]},{hover_cell[1]}")
            tile = model.tiles.get(hover_cell)
            if tile is not None:
                name = state.tileset.name_of(tile.x, tile.y) or f"{tile.x},{tile.y}"
                parts.insert(1, f"Tile: {name}")
            if hover_cell in model.collidables:
                parts.insert(1, "Solid")
        text = font.render(SEPARATOR.join(parts), True, TEXT_COLOR)
        surface.blit(text, text.get_rect(midleft=(rect.x + PANEL_PADDING, rect.centery)))

        if state.message:
            message = font.render(state.message, True, MESSAGE_COLORS[state.message_level])
        elif model.dirty:
            message = font.render("Unsaved changes (Ctrl+S)", True, WARNING_COLOR)
        else:
            message = font.render("All changes saved", True, MUTED_TEXT_COLOR)
        surface.blit(message, message.get_rect(midright=(rect.right - PANEL_PADDING, rect.centery)))
