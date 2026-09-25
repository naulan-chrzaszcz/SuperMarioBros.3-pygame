from typing import Dict, Optional, Tuple

import pygame

from ..constantes import TILE_SIZE
from ..models.entities import EntityType

PLACEHOLDER_COLOR = (255, 0, 255)


class EntityRenderer:
    """Builds (and caches) the zoomed picture of the entity types."""

    def __init__(self) -> None:
        self._sheets: Dict[str, Optional[pygame.Surface]] = {}
        self._cache: Dict[Tuple[Optional[str], int], pygame.Surface] = {}

    def render(self, entity: Optional[EntityType], tile_size: int) -> pygame.Surface:
        """The entity at the zoom of ``tile_size`` (a tile is 16 pixels wide).

        An unknown entity (None) is drawn as a placeholder square."""
        key = (entity.id if entity is not None else None, tile_size)
        surface = self._cache.get(key)
        if surface is None:
            surface = self._build(entity, tile_size)
            self._cache[key] = surface
        return surface

    def _build(self, entity: Optional[EntityType], tile_size: int) -> pygame.Surface:
        picture = self._picture(entity) if entity is not None else None
        if picture is None:
            picture = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(picture, PLACEHOLDER_COLOR, picture.get_rect(), 2)
            pygame.draw.line(picture, PLACEHOLDER_COLOR, (3, 3), (12, 12), 2)
            pygame.draw.line(picture, PLACEHOLDER_COLOR, (12, 3), (3, 12), 2)
        width, height = picture.get_size()
        return pygame.transform.scale(
            picture, (max(1, width * tile_size // TILE_SIZE), max(1, height * tile_size // TILE_SIZE))
        )

    def _picture(self, entity: EntityType) -> Optional[pygame.Surface]:
        sheet = self._sheet(entity)
        if sheet is None:
            return None
        frame = pygame.Rect(entity.frame).clip(sheet.get_rect())
        if frame.width <= 0 or frame.height <= 0:
            return None
        # A 32-bit copy: the palette swap needs exact colors.
        source = pygame.Surface(frame.size, 0, 32)
        source.blit(sheet, (0, 0), frame)
        if entity.palette:
            pixels = pygame.PixelArray(source)
            for old, new in entity.palette:
                pixels.replace(old, new)
            pixels.close()
        if entity.color_key is not None:
            source.set_colorkey(entity.color_key)
        picture = pygame.Surface(source.get_size(), pygame.SRCALPHA)
        picture.blit(source, (0, 0))
        if entity.flip:
            picture = pygame.transform.flip(picture, True, False)
        return picture

    def _sheet(self, entity: EntityType) -> Optional[pygame.Surface]:
        key = str(entity.sheet_path)
        if key not in self._sheets:
            try:
                self._sheets[key] = pygame.image.load(key) if entity.sheet_path is not None else None
            except (pygame.error, FileNotFoundError):
                self._sheets[key] = None
        return self._sheets[key]
