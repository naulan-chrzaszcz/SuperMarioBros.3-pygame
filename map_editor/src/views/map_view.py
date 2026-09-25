from typing import Dict, Optional, Tuple

import pygame

from ..constantes import (
    BORDER_COLOR,
    COLLISION_COLOR,
    GRID_COLOR,
    HOVER_COLOR,
    MAP_BACKGROUND_COLOR,
    OUT_OF_MAP_COLOR,
    REGION_COLOR,
)
from ..models import EditorState, MapEditorModel, Mode, Region, make_region
from .camera import Camera, Cell
from .entity_renderer import EntityRenderer
from .tile_renderer import TileRenderer

RectangleSelection = Tuple[Cell, Cell, int]

PREVIEW_ALPHA = 150
COLLISION_ALPHA = 110
COLLISION_OVERLAY_ALPHA = 55
MIN_GRID_TILE_SIZE = 8
REGION_ALPHA = 45


class MapView:
    """Draws the visible part of the map, the grid, collisions, entities and
    the cursor."""

    def __init__(self, renderer: TileRenderer, entity_renderer: Optional[EntityRenderer] = None) -> None:
        self.renderer = renderer
        self.entity_renderer = entity_renderer or EntityRenderer()
        self._collision_cache: Dict[Tuple[int, int], pygame.Surface] = {}

    def draw(
        self,
        surface: pygame.Surface,
        camera: Camera,
        model: MapEditorModel,
        state: EditorState,
        hover_cell: Optional[Cell],
        rectangle: Optional[RectangleSelection],
        time: float,
    ) -> None:
        viewport = camera.viewport
        size = camera.tile_size
        map_rect = camera.map_rect()

        surface.set_clip(viewport)
        surface.fill(OUT_OF_MAP_COLOR, viewport)
        surface.fill(MAP_BACKGROUND_COLOR, map_rect.clip(viewport))

        columns, rows = camera.visible_cells()
        for row in rows:
            for col in columns:
                tile = model.tiles.get((col, row))
                if tile is not None:
                    surface.blit(
                        self.renderer.render(tile, size, time),
                        camera.cell_to_screen((col, row)),
                    )

        if state.show_collisions or state.mode is Mode.COLLISIONS:
            alpha = COLLISION_ALPHA if state.mode is Mode.COLLISIONS else COLLISION_OVERLAY_ALPHA
            overlay = self._collision_overlay(size, alpha)
            for col, row in model.collidables:
                if col in columns and row in rows:
                    surface.blit(overlay, camera.cell_to_screen((col, row)))

        if state.show_grid and size >= MIN_GRID_TILE_SIZE:
            self._draw_grid(surface, camera, columns, rows, map_rect)
        # Tall entities (a koopa) go above their cell: draw one more row.
        for (col, row), kind in model.entities.items():
            if col in columns and rows.start <= row <= rows.stop:
                self._draw_entity(surface, camera, (col, row), state.entity_type(kind))
        pygame.draw.rect(surface, BORDER_COLOR, map_rect.inflate(2, 2), 1)

        if state.region is not None:
            self._draw_region(surface, camera, state.region)
        if rectangle is not None and state.mode is Mode.SELECT:
            region = model.clip_region(make_region(rectangle[0], rectangle[1]))
            if region is not None:
                self._draw_region(surface, camera, region)
        elif rectangle is not None:
            self._draw_rectangle(surface, camera, model, state, rectangle)
        elif hover_cell is not None and state.pasting:
            self._draw_paste_preview(surface, camera, state, hover_cell, time)
        elif hover_cell is not None and model.contains(hover_cell):
            self._draw_cursor(surface, camera, state, hover_cell, time)
        surface.set_clip(None)

    @staticmethod
    def _region_rect(camera: Camera, region: Region) -> pygame.Rect:
        left, top = camera.cell_to_screen(region[:2])
        right, bottom = camera.cell_to_screen((region[2] + 1, region[3] + 1))
        return pygame.Rect(left, top, right - left, bottom - top)

    def _draw_region(self, surface, camera, region: Region) -> None:
        rect = self._region_rect(camera, region)
        shade = pygame.Surface(rect.size, pygame.SRCALPHA)
        shade.fill((*REGION_COLOR, REGION_ALPHA))
        surface.blit(shade, rect)
        pygame.draw.rect(surface, REGION_COLOR, rect, 2)

    def _draw_paste_preview(self, surface, camera, state, origin: Cell, time) -> None:
        clipboard = state.clipboard
        size = camera.tile_size
        overlay = self._collision_overlay(size, COLLISION_OVERLAY_ALPHA)
        for (col, row), tile, solid in clipboard.cells():
            position = camera.cell_to_screen((origin[0] + col, origin[1] + row))
            # Pasting replaces the cell, so it is previewed as it will look.
            surface.fill(MAP_BACKGROUND_COLOR, (position, (size, size)))
            if tile is not None:
                surface.blit(self.renderer.render(tile, size, time), position)
            if solid:
                surface.blit(overlay, position)
        for (col, row), kind in clipboard.entities.items():
            self._draw_entity(surface, camera, (origin[0] + col, origin[1] + row), state.entity_type(kind))
        region = (origin[0], origin[1], origin[0] + clipboard.columns - 1, origin[1] + clipboard.rows - 1)
        pygame.draw.rect(surface, REGION_COLOR, self._region_rect(camera, region), 2)

    def _draw_grid(self, surface, camera, columns, rows, map_rect) -> None:
        for col in range(columns.start, columns.stop + 1):
            x = camera.cell_to_screen((col, 0))[0]
            pygame.draw.line(surface, GRID_COLOR, (x, map_rect.top), (x, map_rect.bottom - 1))
        for row in range(rows.start, rows.stop + 1):
            y = camera.cell_to_screen((0, row))[1]
            pygame.draw.line(surface, GRID_COLOR, (map_rect.left, y), (map_rect.right - 1, y))

    def _draw_cursor(self, surface, camera, state, cell, time) -> None:
        rect = pygame.Rect(camera.cell_to_screen(cell), (camera.tile_size, camera.tile_size))
        if state.mode is Mode.TILES:
            preview = self.renderer.render(state.selected_tile(), camera.tile_size, time).copy()
            preview.set_alpha(PREVIEW_ALPHA)
            surface.blit(preview, rect)
            pygame.draw.rect(surface, HOVER_COLOR, rect, 1)
        elif state.mode is Mode.SELECT:
            pygame.draw.rect(surface, REGION_COLOR, rect, 1)
        elif state.mode is Mode.ENTITIES:
            if state.selected_entity is not None:
                self._draw_entity(surface, camera, cell, state.selected_entity, PREVIEW_ALPHA)
            pygame.draw.rect(surface, HOVER_COLOR, rect, 1)
        else:
            pygame.draw.rect(surface, COLLISION_COLOR, rect, 2)

    def _draw_rectangle(self, surface, camera, model, state, rectangle) -> None:
        start, end, button = rectangle
        cells = list(model.cells_between(start, end))
        if not cells:
            return
        top_left = camera.cell_to_screen(cells[0])
        bottom_right = camera.cell_to_screen((cells[-1][0] + 1, cells[-1][1] + 1))
        rect = pygame.Rect(top_left, (bottom_right[0] - top_left[0], bottom_right[1] - top_left[1]))

        erase = button != 1
        if state.mode is Mode.TILES and not erase:
            preview = self.renderer.render(state.selected_tile(), camera.tile_size).copy()
            preview.set_alpha(PREVIEW_ALPHA)
            for cell in cells:
                surface.blit(preview, camera.cell_to_screen(cell))
        elif state.mode is Mode.ENTITIES and not erase and state.selected_entity is not None:
            for cell in cells:
                self._draw_entity(surface, camera, cell, state.selected_entity, PREVIEW_ALPHA)
        else:
            shade = pygame.Surface(rect.size, pygame.SRCALPHA)
            color = COLLISION_COLOR if state.mode is Mode.COLLISIONS and not erase else (0, 0, 0)
            shade.fill((*color, 120))
            surface.blit(shade, rect)
        pygame.draw.rect(surface, COLLISION_COLOR if erase else HOVER_COLOR, rect, 2)

    def _draw_entity(self, surface, camera, cell: Cell, entity, alpha: Optional[int] = None) -> None:
        """Entities stand on the bottom of their cell, like in the game."""
        image = self.entity_renderer.render(entity, camera.tile_size)
        if alpha is not None:
            image = image.copy()
            image.set_alpha(alpha)
        x, y = camera.cell_to_screen(cell)
        size = camera.tile_size
        surface.blit(image, (x + (size - image.get_width()) // 2, y + size - image.get_height()))

    def _collision_overlay(self, size: int, alpha: int) -> pygame.Surface:
        key = (size, alpha)
        if key not in self._collision_cache:
            overlay = pygame.Surface((size, size), pygame.SRCALPHA)
            overlay.fill((*COLLISION_COLOR, alpha))
            self._collision_cache[key] = overlay
        return self._collision_cache[key]
