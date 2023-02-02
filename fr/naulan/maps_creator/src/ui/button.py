from typing import Tuple

from pygame import Rect, Surface, draw
from pygame.font import SysFont


class Button(Rect):
    __surface: Surface
    __color_background: Tuple[int, int, int]
    __text_content: Surface
    __font: SysFont

    def __init__(self,
                 color_background: Tuple[int, int, int] = None,
                 surface: Surface = None,
                 x: float = None,
                 y: float = None,
                 width: int = None,
                 height: int = None,
                 text: str = None,
                 text_color: Tuple[int, int, int] = None):
        super().__init__(self)

        self.__surface = surface
        self.__color_background = color_background
        self.x = int(x)
        self.y = int(y)
        self.width = width
        self.height = height

        self.__font = SysFont("arial", height//2)
        self.__text_content = self.__font.render(text, True, text_color)

    def blit(self):
        draw.rect(self.__surface,
                  self.__color_background,
                  self,
                  self.width)
        self.__surface.blit(self.__text_content, (self.x + (self.width/4), self.y + (self.height/4)))

