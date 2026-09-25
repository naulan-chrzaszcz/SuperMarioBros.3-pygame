from typing import List, Optional, Tuple

import pygame

from ..constantes import (
    BORDER_COLOR,
    BUTTON_GAP,
    BUTTON_HEIGHT,
    HOVER_COLOR,
    MAX_SIDEBAR_WIDTH,
    MIN_SIDEBAR_WIDTH,
    MUTED_TEXT_COLOR,
    PANEL_COLOR,
    PANEL_PADDING,
    PREVIEW_SIZE,
    SELECTION_COLOR,
    TEXT_COLOR,
    TILE_SIZE,
    UNDECLARED_TILE_SHADE,
    WARNING_COLOR,
)
from ..models import EditorState
from .tile_renderer import TileRenderer
from .widgets import Button

MAX_TILESET_SCALE = 4
HELP_SEPARATOR = "   "
HELP_LINES = (
    "Left: paint   Right: erase",
    "Shift + drag: fill a rectangle",
    "Middle click: pick   Middle drag: pan",
    "Wheel: scroll   Shift + wheel: sideways",
    "Ctrl + wheel, + / -: zoom   Home: fit",
    "Arrows: move   R: rotate",
    "C: tiles / collisions   S: select",
    "Ctrl+C / X / V: copy / cut / paste",
    "Ctrl+A: select all   Del: clear",
    "G: grid   O: solid overlay",
    "Ctrl+Z / Ctrl+Y: undo / redo",
    "Ctrl+S: save   Esc: close the map",
    "F5: play the map (from the game)",
)


class SidebarView:
    """Selected tile preview, tool buttons, tileset picker and shortcuts help."""

    def __init__(self, state: EditorState, renderer: TileRenderer) -> None:
        self.state = state
        self.renderer = renderer
        self.rows: List[List[Button]] = []
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.preview_rect = pygame.Rect(0, 0, PREVIEW_SIZE, PREVIEW_SIZE)
        self.tileset_rect = pygame.Rect(0, 0, 0, 0)
        self.tileset_scale = 1
        self.help_top = 0
        self._scaled_tileset: Optional[pygame.Surface] = None
        self._undeclared_shade: Optional[pygame.Surface] = None

    @property
    def buttons(self) -> List[Button]:
        return [button for row in self.rows for button in row]

    def set_rows(self, rows: List[List[Button]]) -> None:
        self.rows = rows
        if self.rect.width:
            self.layout(self.rect)

    def preferred_width(self) -> int:
        width = self.state.tileset.image.get_width() * 2 + 2 * PANEL_PADDING
        return min(max(width, MIN_SIDEBAR_WIDTH), MAX_SIDEBAR_WIDTH)

    def layout(self, rect: pygame.Rect) -> None:
        self.rect = pygame.Rect(rect)
        inner_width = self.rect.width - 2 * PANEL_PADDING
        left = self.rect.x + PANEL_PADDING
        y = self.rect.y + PANEL_PADDING

        self.preview_rect.topleft = (left, y)
        y += PREVIEW_SIZE + PANEL_PADDING

        for row in self.rows:
            weights = [3 if button.on_click is None else 2 for button in row]
            available = inner_width - BUTTON_GAP * (len(row) - 1)
            x = left
            for button, weight in zip(row, weights):
                width = available * weight // sum(weights)
                button.rect = pygame.Rect(x, y, width, BUTTON_HEIGHT)
                x += width + BUTTON_GAP
            y += BUTTON_HEIGHT + BUTTON_GAP

        y += PANEL_PADDING + BUTTON_HEIGHT  # Room for the "Tileset" title.
        image = self.state.tileset.image
        help_height = len(HELP_LINES) * 18 + PANEL_PADDING
        available_height = self.rect.bottom - y - PANEL_PADDING - help_height
        scale = min(inner_width // image.get_width(), MAX_TILESET_SCALE)
        while scale > 1 and image.get_height() * scale > available_height:
            scale -= 1
        self.tileset_scale = max(scale, 1)
        self.tileset_rect = pygame.Rect(
            left,
            y,
            min(image.get_width() * self.tileset_scale, inner_width),
            image.get_height() * self.tileset_scale,
        )
        self.help_top = self.tileset_rect.bottom + PANEL_PADDING
        self._scaled_tileset = None
        self._undeclared_shade = None

    def tileset_cell_at(self, position: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        if not self.tileset_rect.collidepoint(position):
            return None
        cell_size = TILE_SIZE * self.tileset_scale
        x = (position[0] - self.tileset_rect.x) // cell_size
        y = (position[1] - self.tileset_rect.y) // cell_size
        return (x, y) if self.state.tileset.contains(x, y) else None

    def draw(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        mouse: Tuple[int, int],
        time: float,
    ) -> None:
        pygame.draw.rect(surface, PANEL_COLOR, self.rect)
        pygame.draw.line(surface, BORDER_COLOR, self.rect.topleft, self.rect.bottomleft)
        surface.set_clip(self.rect)

        self._draw_selected_tile(surface, font, time)
        for button in self.buttons:
            button.draw(surface, font, mouse)
        self._draw_tileset(surface, font, mouse)

        y = self.help_top
        for line in self._help_lines(font):
            if y + font.get_linesize() > self.rect.bottom:
                break
            surface.blit(font.render(line, True, MUTED_TEXT_COLOR), (self.rect.x + PANEL_PADDING, y))
            y += 18
        surface.set_clip(None)

    def _help_lines(self, font) -> List[str]:
        """Shortcut hints packed into lines that fit the sidebar width."""
        width = self.rect.width - 2 * PANEL_PADDING
        lines: List[str] = []
        for line in HELP_LINES:
            current = ""
            for part in line.split(HELP_SEPARATOR):
                candidate = f"{current}{HELP_SEPARATOR}{part}" if current else part
                if current and font.size(candidate)[0] > width:
                    lines.append(current)
                    current = part
                else:
                    current = candidate
            lines.append(current)
        return lines

    def _draw_selected_tile(self, surface, font, time) -> None:
        state = self.state
        preview = self.renderer.render(state.selected_tile(), PREVIEW_SIZE, time)
        surface.fill((0, 0, 0), self.preview_rect)
        surface.blit(preview, self.preview_rect)
        pygame.draw.rect(surface, BORDER_COLOR, self.preview_rect.inflate(2, 2), 1)

        x = self.preview_rect.right + PANEL_PADDING
        y = self.preview_rect.y
        name = state.selected_name or ("Undeclared tile" if state.tileset.has_metadata else "Tile")
        lines = [
            (name, TEXT_COLOR),
            (f"Sheet {state.selection_x},{state.selection_y}   Rotation {state.rotation}", MUTED_TEXT_COLOR),
            (self._frames_text(), MUTED_TEXT_COLOR),
        ]
        if not state.selection_declared:
            reason = state.tileset.missing_reason
            lines.append((reason[0].upper() + reason[1:], WARNING_COLOR))
        for text, color in lines:
            surface.blit(font.render(text, True, color), (x, y))
            y += font.get_linesize()

    def _frames_text(self) -> str:
        if self.state.frames_x > 1:
            return f"Animated: {self.state.frames_x} frames (X)"
        if self.state.frames_y > 1:
            return f"Animated: {self.state.frames_y} frames (Y)"
        return "Static"

    def _draw_tileset(self, surface, font, mouse) -> None:
        title_y = self.tileset_rect.y - BUTTON_HEIGHT
        surface.blit(
            font.render("Tileset  (click, wheel to browse)", True, TEXT_COLOR),
            (self.tileset_rect.x, title_y + 4),
        )
        surface.fill((0, 0, 0), self.tileset_rect)
        surface.blit(self._tileset_image(), self.tileset_rect)
        if self.state.tileset.has_metadata:
            surface.blit(self._undeclared_overlay(), self.tileset_rect)

        cell_size = TILE_SIZE * self.tileset_scale
        hovered = self.tileset_cell_at(mouse)
        if hovered is not None:
            rect = pygame.Rect(
                self.tileset_rect.x + hovered[0] * cell_size,
                self.tileset_rect.y + hovered[1] * cell_size,
                cell_size,
                cell_size,
            )
            pygame.draw.rect(surface, HOVER_COLOR, rect, 1)

        state = self.state
        selection = pygame.Rect(
            self.tileset_rect.x + state.selection_x * cell_size,
            self.tileset_rect.y + state.selection_y * cell_size,
            cell_size * state.frames_x,
            cell_size * state.frames_y,
        )
        pygame.draw.rect(surface, SELECTION_COLOR, selection, 2)
        pygame.draw.rect(surface, BORDER_COLOR, self.tileset_rect.inflate(2, 2), 1)

    def _tileset_image(self) -> pygame.Surface:
        if self._scaled_tileset is None:
            image = self.state.tileset.image
            self._scaled_tileset = pygame.transform.scale(
                image,
                (image.get_width() * self.tileset_scale, image.get_height() * self.tileset_scale),
            )
        return self._scaled_tileset

    def _undeclared_overlay(self) -> pygame.Surface:
        """Darkens the sheet cells that the game cannot load."""
        if self._undeclared_shade is None:
            tileset = self.state.tileset
            cell_size = TILE_SIZE * self.tileset_scale
            shade = pygame.Surface(self._tileset_image().get_size(), pygame.SRCALPHA)
            for y in range(tileset.rows):
                for x in range(tileset.columns):
                    if not tileset.is_declared(x, y):
                        shade.fill(UNDECLARED_TILE_SHADE, (x * cell_size, y * cell_size, cell_size, cell_size))
            self._undeclared_shade = shade
        return self._undeclared_shade
