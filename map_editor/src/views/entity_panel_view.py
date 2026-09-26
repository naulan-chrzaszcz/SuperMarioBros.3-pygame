"""Floating panel that tunes the settings of one entity placed on the map."""

from __future__ import annotations

from typing import List, Optional, Tuple

import pygame

from ..constants import (
    BORDER_COLOR,
    BUTTON_GAP,
    BUTTON_HEIGHT,
    MUTED_TEXT_COLOR,
    PANEL_COLOR,
    PANEL_PADDING,
    TEXT_COLOR,
)
from ..models.entity_panel import EntityPanel
from .widgets import Button, ListBox

PANEL_WIDTH = 300
PANEL_MARGIN = 16
ROW_HEIGHT = 24
MAX_ROWS = 12
HINT_HEIGHT = 18
HINT = "Left / Right: change   Backspace: default"


class EntityPanelView:
    """Title, scrollable list of settings and buttons of the tuned entity.

    It floats over the map, next to the sidebar, and is drawn only while an
    entity is being tuned (:class:`EntityPanel`).
    """

    def __init__(self, panel: EntityPanel) -> None:
        self.panel = panel
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.list = ListBox(panel.rows, lambda: panel.index, panel.select, ROW_HEIGHT)
        self.buttons: List[Button] = [
            Button("<", lambda: panel.change(-1)),
            Button(lambda: panel.selected_label),
            Button(">", lambda: panel.change(1)),
            Button("Default", panel.reset),
            Button("Reset all", panel.reset_all),
            Button("Close  (Esc)", panel.close),
        ]

    @property
    def visible(self) -> bool:
        return self.panel.visible

    def layout(self, map_rect: pygame.Rect) -> None:
        """Places the panel in the top-right corner of the map area."""
        rows = min(max(len(self.panel.rows()), 1), MAX_ROWS)
        height = (
            PANEL_PADDING * 3 + BUTTON_HEIGHT * 3 + BUTTON_GAP + HINT_HEIGHT + rows * ROW_HEIGHT
        )
        width = min(PANEL_WIDTH, max(map_rect.width - 2 * PANEL_MARGIN, 0))
        height = min(height, max(map_rect.height - 2 * PANEL_MARGIN, 0))
        self.rect = pygame.Rect(
            map_rect.right - width - PANEL_MARGIN, map_rect.y + PANEL_MARGIN, width, height
        )
        inner = self.rect.width - 2 * PANEL_PADDING
        left = self.rect.x + PANEL_PADDING
        y = self.rect.y + PANEL_PADDING + BUTTON_HEIGHT  # Room for the title.
        list_height = (
            self.rect.bottom - y - PANEL_PADDING * 2 - HINT_HEIGHT - 2 * BUTTON_HEIGHT - BUTTON_GAP
        )
        self.list.rect = pygame.Rect(left, y, inner, max(list_height, 0))
        y = self.list.rect.bottom + PANEL_PADDING
        changer = self.buttons[:3]
        widths = (BUTTON_HEIGHT * 2, inner - 2 * (BUTTON_HEIGHT * 2 + BUTTON_GAP), BUTTON_HEIGHT * 2)
        x = left
        for button, width in zip(changer, widths):
            button.rect = pygame.Rect(x, y, width, BUTTON_HEIGHT)
            x += width + BUTTON_GAP
        y += BUTTON_HEIGHT + BUTTON_GAP
        x = left
        for button in self.buttons[3:]:
            width = (inner - 2 * BUTTON_GAP) // 3
            button.rect = pygame.Rect(x, y, width, BUTTON_HEIGHT)
            x += width + BUTTON_GAP

    def draw(
        self, surface: pygame.Surface, font: pygame.font.Font, mouse: Tuple[int, int]
    ) -> None:
        if not self.visible:
            return
        pygame.draw.rect(surface, PANEL_COLOR, self.rect, border_radius=6)
        pygame.draw.rect(surface, BORDER_COLOR, self.rect, 1, 6)
        title = font.render(self.panel.title, True, TEXT_COLOR)
        surface.blit(title, (self.rect.x + PANEL_PADDING, self.rect.y + PANEL_PADDING))
        if self.panel.keys:
            self.list.ensure_visible(self.panel.index)
            self.list.draw(surface, font, mouse)
            for button in self.buttons:
                button.draw(surface, font, mouse)
        else:
            text = font.render("This entity has no setting to tune", True, MUTED_TEXT_COLOR)
            surface.blit(text, text.get_rect(center=self.list.rect.center))
            self.buttons[-1].draw(surface, font, mouse)
        hint = font.render(HINT, True, MUTED_TEXT_COLOR)
        surface.blit(hint, (self.rect.x + PANEL_PADDING, self.rect.bottom - PANEL_PADDING - HINT_HEIGHT))

    def click(self, position: Tuple[int, int]) -> bool:
        """Handles a click on the panel; False when it was somewhere else."""
        if not self.visible or not self.rect.collidepoint(position):
            return False
        for button in self.buttons:
            if button.click(position):
                return True
        self.list.click(position)
        return True

    def scroll(self, delta: int, mouse: Tuple[int, int]) -> bool:
        if not self.visible or not self.list.rect.collidepoint(mouse):
            return False
        self.list.scroll_by(delta)
        return True

    def hovered(self, position: Optional[Tuple[int, int]]) -> bool:
        return self.visible and position is not None and self.rect.collidepoint(position)
