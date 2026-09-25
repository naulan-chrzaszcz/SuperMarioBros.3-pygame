from typing import Optional, Tuple

import pygame

MAP_PANEL = "map"
COMMANDS_PANEL = "commands"
TILES_PANEL = "tiles"

BACKGROUND_COLOR = (32, 32, 32)
BORDER_COLOR = (96, 96, 96)


class ApplicationView:
    """Composes the map, the settings and the tile selector in one window."""

    def __init__(
        self,
        title: str,
        map_view: pygame.Surface,
        commands_surface: pygame.Surface,
        tile_selection_surface: pygame.Surface,
        gap: int,
    ) -> None:
        self.title = title
        self.map_view = map_view
        self.commands_surface = commands_surface
        self.tile_selection_surface = tile_selection_surface

        self.map_rect = pygame.Rect((0, 0), map_view.get_size())
        sidebar_x = self.map_rect.right + gap
        self.commands_rect = pygame.Rect(
            (sidebar_x, gap), commands_surface.get_size()
        )

        tiles_y = self.commands_rect.bottom + gap
        sheet_width, sheet_height = tile_selection_surface.get_size()
        available_width = self.commands_rect.width
        available_height = max(self.map_rect.height - tiles_y - gap, sheet_height)
        self.tile_scale = max(
            1,
            min(available_width // sheet_width, available_height // sheet_height),
        )
        self.tiles_rect = pygame.Rect(
            sidebar_x,
            tiles_y,
            min(sheet_width * self.tile_scale, available_width),
            min(sheet_height * self.tile_scale, available_height),
        )

        self.size = (
            self.commands_rect.right + gap,
            max(self.map_rect.height, self.tiles_rect.bottom + gap),
        )
        self.screen = pygame.display.set_mode(self.size)
        self._caption = None
        self.set_caption(title)

    def set_caption(self, caption: str) -> None:
        if caption != self._caption:
            pygame.display.set_caption(caption)
            self._caption = caption

    def panel_at(self, position: Tuple[int, int]) -> Optional[str]:
        if self.map_rect.collidepoint(position):
            return MAP_PANEL
        if self.commands_rect.collidepoint(position):
            return COMMANDS_PANEL
        if self.tiles_rect.collidepoint(position):
            return TILES_PANEL
        return None

    def to_local(self, panel: str, position: Tuple[int, int]) -> Tuple[int, int]:
        if panel == MAP_PANEL:
            rect = self.map_rect
        elif panel == COMMANDS_PANEL:
            rect = self.commands_rect
        else:
            return (
                (position[0] - self.tiles_rect.x) // self.tile_scale,
                (position[1] - self.tiles_rect.y) // self.tile_scale,
            )
        return position[0] - rect.x, position[1] - rect.y

    def draw(self) -> None:
        self.screen.fill(BACKGROUND_COLOR)
        self.screen.blit(self.map_view, self.map_rect)
        self.screen.blit(self.commands_surface, self.commands_rect)

        tiles = pygame.transform.scale_by(
            self.tile_selection_surface, self.tile_scale
        )
        self.screen.blit(
            tiles, self.tiles_rect, pygame.Rect((0, 0), self.tiles_rect.size)
        )

        pygame.draw.line(
            self.screen,
            BORDER_COLOR,
            (self.map_rect.right, 0),
            (self.map_rect.right, self.map_rect.bottom),
        )
        pygame.draw.rect(self.screen, BORDER_COLOR, self.tiles_rect.inflate(2, 2), 1)
        pygame.display.flip()
