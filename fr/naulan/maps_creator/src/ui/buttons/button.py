from typing import Tuple

from pygame import Surface, draw, event
from pygame.font import SysFont
from pygame.locals import *

from fr.naulan.maps_creator.src.creator import Creator
from fr.naulan.maps_creator.src.ui.buttons.action.button_action import ButtonAction


class Button(Rect):
    __surface: Surface
    color_background: Tuple[int, int, int]
    __text_content: Surface
    __font: SysFont
    __action: ButtonAction

    def __init__(self,
                 color_background: Tuple[int, int, int] = None,
                 surface: Surface = None,
                 x: float = None,
                 y: float = None,
                 width: int = None,
                 height: int = None,
                 text: str = None,
                 text_color: Tuple[int, int, int] = None,
                 action: ButtonAction = None):
        super().__init__(self)

        self.__surface = surface
        self.color_background = color_background
        self.x = int(x)
        self.y = int(y)
        self.width = width
        self.height = height

        self.__font = SysFont("arial", height//2)
        self.__text_content = self.__font.render(text, True, text_color)
        self.__action = action
        self.__action(self)

    def event(self):
        for e in event.get():
            if e.type == MOUSEBUTTONDOWN:
                environment = Creator.get_instance()
                if environment.mouse_pointer.colliderect(self):
                    self.onclick()

    def onclick(self):
        self.__action.action()

    def blit(self):
        draw.rect(self.__surface,
                  self.color_background,
                  self,
                  self.width)
        self.__surface.blit(self.__text_content,
                            (self.x + (self.width/2) - (self.__text_content.get_width()/2),
                             self.y + (self.height/2) - (self.__text_content.get_height()/2)))
