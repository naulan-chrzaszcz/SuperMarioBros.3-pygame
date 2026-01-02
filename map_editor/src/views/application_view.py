import pygame


class ApplicationView:
    def __init__(self,
                 map_editor_surface: pygame.Surface,
                 tile_selection_surface: pygame.Surface,
                 commands_surface: pygame.Surface):
        self.map_editor_surface = map_editor_surface
        self.tile_selection_surface = tile_selection_surface
        self.commands_surface = commands_surface

        pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("SuperMarioBros3 - Map editor")

    def show(self):
        pass
