from src.constantes import TILE_SIZE

import pygame


class MapEditorView(pygame.Surface):
    def __init__(self, size: tuple) -> None:
        super().__init__((1280, 720))
        self.tile_surface = pygame.Surface(size)
        self.cursor_surface = pygame.Surface(size, pygame.SRCALPHA)
        self.collidable_tile_surface = pygame.Surface(size, pygame.SRCALPHA)
        self.collidable_tile_surface.set_alpha(50)
        self.grid_surface = pygame.Surface(size, pygame.SRCALPHA)

    def draw(self, model, camera) -> None:
        self.tile_surface.fill((0, 0, 0))
        self.cursor_surface.fill((0, 0, 0))
        self.collidable_tile_surface.fill((0, 0, 0, 0))
        self.grid_surface.fill((0, 0, 0, 0))

        for pos, tile in model.tiles.items():
            self.view.tile_surface.blit(tile.surface, pos)
        for pos, rect in model.collidables.items():
            pygame.draw.rect(self.collidable_tile_surface, (255, 0, 0), rect)

        for line in range(self.tile_surface.get_height() // TILE_SIZE):
            pygame.draw.line(
                self.grid_surface,
                (64, 64, 64),
                (0, line * TILE_SIZE),
                (self.tile_surface.get_width(), line * TILE_SIZE),
            )

        for row in range(self.tile_surface.get_width() // TILE_SIZE):
            pygame.draw.line(
                self.grid_surface,
                (64, 64, 64),
                (row * TILE_SIZE, 0),
                (row * TILE_SIZE, self.grid_surface.get_height()),
            )

        if not cmd_surface.collidable_btn.value:
            # Display tile selection following the cursor
            self.tile_surface.blit(
                pygame.transform.rotate(
                    model.sheet.subsurface(
                        (
                            (
                                self.model.tile_sheet_selection_x * TILE_SIZE,
                                self.model.tile_sheet_selection_y * TILE_SIZE,
                            ),
                            (TILE_SIZE, TILE_SIZE),
                        )
                    ),
                    self.model.tile_rotation,
                ),
                (self.model.tile_selection_x, self.model.tile_selection_y),
            )
        else:
            pygame.draw.rect(
                map_surface_collidable,
                (255, 0, 0),
                pygame.Rect(map_tile_selection_x, map_tile_selection_y, 16, 16),
            )

        self.blit(
            pygame.transform.scale(
                self.tile_surface.subsurface(camera), self.get_size()
            ),
            (0, 0),
        )
        self.blit(
            pygame.transform.scale(
                self.cursor_surface.subsurface(camera), self.get_size()
            ),
            (0, 0),
        )
        self.blit(
            pygame.transform.scale(
                self.collidable_tile_surface.subsurface(camera), self.get_size()
            ),
            (0, 0),
        )
        self.blit(
            pygame.transform.scale(
                self.grid_surface.subsurface(camera), self.get_size()
            ),
            (0, 0),
        )

