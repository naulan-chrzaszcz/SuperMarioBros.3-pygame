import pygame

from src.constantes import TILE_SIZE
from src.controllers import CameraController
from src.outputs.tile import Tile


class MapEditorController:
    def __init__(self, model, view) -> None:
        self.model = model
        self.view = view
        self.camera_controller = CameraController(
            0,
            0,
            TILE_SIZE * 29,
            TILE_SIZE * 15,
            self.view.get_width(),
            self.view.get_height(),
        )

        self.scale_x = self.camera_controller.width / 1280
        self.scale_y = self.camera_controller.height / 720

    def handle_event(self, event):
        self.camera_controller.handle_event(event)

        if event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_x = mouse_x * self.scale_x // TILE_SIZE
            mouse_y = mouse_y * self.scale_y // TILE_SIZE
            self.model.tile_selection_x = mouse_x * TILE_SIZE + self.camera_controller.left
            self.model.tile_selection_y = mouse_y * TILE_SIZE + self.camera_controller.top
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not cmd_surface.collidable_btn.value:
                tile = Tile(
                    tile_selection_surface.selection_x,
                    tile_selection_surface.selection_y,
                    cmd_surface.frames_x_btn.value,
                    cmd_surface.frames_y_btn.value,
                    cmd_surface.rotation_btn.value,
                )
                tile.surface = pygame.transform.rotate(
                    sheet.subsurface(
                        (tile.x * TILE_SIZE, tile.y * TILE_SIZE),
                        (TILE_SIZE, TILE_SIZE),
                    ).copy(),
                    cmd_surface.rotation_btn.value,
                )
                self.model.tiles[(map_tile_selection_x, map_tile_selection_y)] = tile
            else:
                self.model.collidables[(map_tile_selection_x, map_tile_selection_y)] = (
                    pygame.Rect(map_tile_selection_x, map_tile_selection_y, 16, 16)
                )

    def update(self) -> None:
        self.view.draw(self.model, self.camera_controller)

