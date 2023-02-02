from typing import Tuple

from pygame import Surface

from fr.naulan.maps_creator.src.ui.button import Button


class ButtonBuilder(object):
    __button: Button
    __color_background: Tuple[int, int, int]
    __surface: Surface
    __width: int
    __height: int
    __x: float
    __y: float
    __text_content: str

    @property
    def button(self):
        return self.__button

    @button.setter
    def button(self, button: Button):
        raise Exception()

    @button.getter
    def button(self) -> Button:
        self.__button = Button(self.__color_background,
                               self.__surface,
                               self.__x,
                               self.__y,
                               self.__width,
                               self.__height,
                               self.__text_content)
        return self.__button

    def set_color_background(self, color: Tuple[int, int, int]):
        self.__color_background = color

    def set_surface(self, surface: Surface):
        self.__surface = surface

    def set_width(self, width: int):
        self.__width = width

    def set_height(self, height: int):
        self.__height = height

    def set_x(self, x: float):
        self.__x = x

    def set_y(self, y: float):
        self.__y = y

    def set_text(self, text: str):
        self.__text_content = text
