import pygame

from dataclasses import dataclass

from src.constantes import TILE_SIZE


@dataclass
class TileSelectionModel:
    sheet: pygame.Surface
    selection_x = 0
    selection_y = 0
    selection_rect = pygame.Rect(
        selection_x, selection_y, TILE_SIZE, TILE_SIZE
    )

