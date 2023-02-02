from typing import Tuple

from pygame import Surface

from fr.naulan.maps_creator.src.ui.buttons.button import Button
from fr.naulan.maps_creator.src.ui.buttons.action.button_action import ButtonAction


class ButtonBuilder(object):
    __button: Button
    __color_background: Tuple[int, int, int]
    __surface: Surface
    __width: int
    __height: int
    __x: float
    __y: float
    __text_content: str
    __text_color: Tuple[int, int, int]
    __action: ButtonAction

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
                               self.__text_content,
                               self.__text_color,
                               self.__action)
        return self.__button

    def set_color_background(self, color: Tuple[int, int, int]):
        self.__color_background = color

    def set_surface(self, surface: Surface):
        self.__surface = surface

    def set_action(self, action: ButtonAction):
        self.__action = action

    def set_width(self, width: int):
        self.__width = width

    def set_height(self, height: int):
        self.__height = height

    def set_x(self, x: float):
        self.__x = x

    def set_y(self, y: float):
        self.__y = y

    def set_text(self, text: str, color: Tuple[int, int, int]):
        self.__text_content = text
        self.__text_color = color
