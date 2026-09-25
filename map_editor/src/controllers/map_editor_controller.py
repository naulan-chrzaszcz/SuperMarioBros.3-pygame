import pygame

from ..constantes import TILE_SIZE
from ..outputs.tile import Tile
from .camera_controller import CameraController


class MapEditorController:
    def __init__(self, model, view, commands, tile_selection) -> None:
        self.model = model
        self.view = view
        self.commands = commands
        self.tile_selection = tile_selection
        self.camera_controller = CameraController(
            0,
            0,
            min(TILE_SIZE * 29, self.model.width),
            min(TILE_SIZE * 15, self.model.height),
            self.model.width,
            self.model.height,
        )

        self.scale_x = self.camera_controller.width / self.view.get_width()
        self.scale_y = self.camera_controller.height / self.view.get_height()

    def handle_event(self, event) -> None:
        self.camera_controller.handle_event(event)

        if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
            self._update_selection(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 3):
            self._edit_cell(event.button)
        elif event.type == pygame.MOUSEMOTION:
            if event.buttons[0]:
                self._edit_cell(1)
            elif event.buttons[2]:
                self._edit_cell(3)

    def update(self) -> None:
        preview_tile = self._create_selected_tile()
        self.view.draw(
            self.model,
            self.camera_controller,
            preview_tile,
            self.commands.collidable_btn.value,
        )

    def _update_selection(self, position) -> None:
        mouse_x = int(position[0] * self.scale_x)
        mouse_y = int(position[1] * self.scale_y)
        selection_x = (
            mouse_x // TILE_SIZE * TILE_SIZE + self.camera_controller.left
        )
        selection_y = (
            mouse_y // TILE_SIZE * TILE_SIZE + self.camera_controller.top
        )
        self.model.tile_selection_x = min(selection_x, self.model.width - TILE_SIZE)
        self.model.tile_selection_y = min(selection_y, self.model.height - TILE_SIZE)

    def _edit_cell(self, button: int) -> None:
        col = self.model.tile_selection_x // TILE_SIZE
        row = self.model.tile_selection_y // TILE_SIZE
        if self.commands.collidable_btn.value:
            self.model.set_collidable(col, row, button == 1)
        elif button == 1:
            self.model.add_tile(col, row, self._create_selected_tile())
        else:
            self.model.remove_tile(col, row)

    def _create_selected_tile(self) -> Tile:
        tile = Tile(
            int(self.tile_selection.selection_x),
            int(self.tile_selection.selection_y),
            int(self.commands.frames_x_btn_model.value),
            int(self.commands.frames_y_btn_model.value),
            int(self.commands.rotation_btn_model.value),
        )
        tile.surface = self.model.create_tile_surface(tile)
        return tile
