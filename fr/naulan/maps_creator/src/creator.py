from pygame import Surface, display, Rect, mouse
from pygame.time import Clock

from pygame.locals import *


class Creator(object):
    __instance = None

    screen: Surface
    display: Surface
    mouse_pointer: Rect
    clock: Clock

    def __new__(cls, screen: Surface, _display: Surface):
        if cls.__instance is None:
            cls.__instance = super(Creator, cls).__new__(cls)
        return cls.__instance

    def __init__(self, screen: Surface, _display: Surface):
        self.screen = screen
        self.display = _display
        self.mouse_pointer = Rect(0, 0, 5, 5)
        self.clock = Clock()

    @staticmethod
    def get_instance():
        return Creator.__instance

    def run(self):
        # Should make this import here because the creator class is not initialized
        from fr.naulan.maps_creator.src.ui.buttons.button_builder import ButtonBuilder
        from fr.naulan.maps_creator.src.ui.buttons.action.change_color_button_action import ChangeColorButtonAction

        button_builder = ButtonBuilder()
        button_builder.set_x(50)
        button_builder.set_y(50)
        button_builder.set_text("Click !", (255, 255, 255))
        button_builder.set_color_background((255, 185, 45))
        button_builder.set_surface(self.screen)
        button_builder.set_height(50)
        button_builder.set_width(100)
        button_builder.set_action(ChangeColorButtonAction())
        button = button_builder.button

        while True:
            self.screen.fill((0, 0, 0))
            self.clock.tick(60)

            x, y = mouse.get_pos()
            self.mouse_pointer.update(x, y, self.mouse_pointer.width, self.mouse_pointer.height)

            button.event()
            button.blit()
            display.update()
