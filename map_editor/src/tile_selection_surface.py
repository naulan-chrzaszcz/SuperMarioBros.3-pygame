from .constantes import TILE_SIZE, TILE_SELECTION_COLOR, TILE_SELECTION_FRAME_WIDTH

import pygame


class TileSelectionSurface(pygame.Surface):
    def __init__(self, sheet_image: pygame.Surface) -> None:
        super().__init__((sheet_image.get_width(), sheet_image.get_height()))

        self.sheet_image = sheet_image
        self.selection_x = 0
        self.selection_y = 0
        self.selection_rect = pygame.Rect(
            self.selection_x, self.selection_y, TILE_SIZE, TILE_SIZE
        )

    def handle_event(self, event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.selection_x = mouse_x // TILE_SIZE
            self.selection_y = mouse_y // TILE_SIZE
        if event.type == pygame.MOUSEWHEEL:
            self.selection_x = min(
                self.sheet_image.width // TILE_SIZE - 1,
                self.selection_x + event.precise_x,
            )
            self.selection_y = min(
                self.get_height() // TILE_SIZE - 1,
                self.selection_y + event.precise_y,
            )
            self.selection_x = max(self.selection_x, 0)
            self.selection_y = max(self.selection_y, 0)

        self.selection_rect.update(
            self.selection_x * TILE_SIZE,
            self.selection_y * TILE_SIZE,
            TILE_SIZE,
            TILE_SIZE,
        )

    def draw(self) -> None:
        self.fill((0, 0, 0))
        self.blit(self.sheet_image, (0, 0))
        pygame.draw.rect(
            self,
            TILE_SELECTION_COLOR,
            self.selection_rect,
            TILE_SELECTION_FRAME_WIDTH,
        )
