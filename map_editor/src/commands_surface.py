from typing import Any, Optional, Tuple

from .constantes import (
    BUTTON_GAP,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
    BUTTON_COLOR,
    FONT_SIZE,
    COLLIDABLE_COLOR_OFF_BTN,
    COLLIDABLE_COLOR_ON_BTN,
)
from .models import ButtonModel
from .views import ButtonView
from .controllers import ButtonController


import pygame


class CommandsSurface(pygame.Surface):
    button_controllers = []
    button_views = []

    def __init__(self, width, height):
        super().__init__((width, height))
        self.font = pygame.font.SysFont("Arial", FONT_SIZE)

        self.rotation_btn_model = self.create_button(
            BUTTON_GAP,
            BUTTON_GAP,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            BUTTON_COLOR,
            text="ROTATION: 0",
            value=0,
        )

        def rotation_btn_on_click():
            self.rotation_btn_model.value += 90
            self.rotation_btn_model.value %= 360
            self.rotation_btn_model.text = f"ROTATION: {self.rotation_btn_model.value}"

        self.rotation_btn_model.on_click = rotation_btn_on_click

        self.frames_x_btn_model = self.create_button(
            self.rotation_btn_model.x,
            self.rotation_btn_model.y + BUTTON_HEIGHT + BUTTON_GAP,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            BUTTON_COLOR,
            text="FRAMES X: 1",
            value=1,
        )

        self.frames_x_btn_up_model = self.create_button(
            self.frames_x_btn_model.x + self.frames_x_btn_model.width + BUTTON_GAP,
            self.rotation_btn_model.y + BUTTON_HEIGHT + BUTTON_GAP,
            BUTTON_WIDTH / 4,
            BUTTON_HEIGHT / 2,
            BUTTON_COLOR,
            text="+",
        )

        def frames_x_btn_up_on_click():
            self.frames_x_btn_model.value += 1
            self.frames_x_btn_model.text = f"FRAMES X: {self.frames_x_btn_model.value}"

        self.frames_x_btn_up_model.on_click = frames_x_btn_up_on_click

        self.frames_x_btn_down_model = self.create_button(
            self.frames_x_btn_model.x + self.frames_x_btn_model.width + BUTTON_GAP,
            self.frames_x_btn_up_model.y + self.frames_x_btn_model.height,
            BUTTON_WIDTH / 4,
            BUTTON_HEIGHT / 2,
            BUTTON_COLOR,
            text="-",
        )

        def frames_x_btn_down_on_click():
            self.frames_x_btn_model.value = max(self.frames_x_btn_model.value - 1, 1)
            self.frames_x_btn_model.text = f"FRAMES X: {self.frames_x_btn_model.value}"

        self.frames_x_btn_down_model.on_click = frames_x_btn_down_on_click

        self.frames_y_btn_model = self.create_button(
            self.frames_x_btn_model.x,
            self.frames_x_btn_down_model.y + BUTTON_HEIGHT / 2 + BUTTON_GAP,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            BUTTON_COLOR,
            text="FRAMES Y: 1",
            value=1,
        )

        self.frames_y_btn_up = self.create_button(
            self.frames_x_btn_down_model.x,
            self.frames_x_btn_down_model.x
            + self.frames_x_btn_down_model.height
            + BUTTON_GAP,
            BUTTON_WIDTH / 4,
            BUTTON_HEIGHT / 2,
            BUTTON_COLOR,
            text="+",
        )
        self.frames_y_btn_up.text = "+"

        def frames_y_btn_up_on_click():
            self.frames_y_btn_model.value += 1
            self.frames_y_btn_model.text = f"FRAMES Y: {self.frames_y_btn_model.value}"

        self.frames_y_btn_up.on_click = frames_y_btn_up_on_click

        self.frames_y_btn_down = self.create_button(
            self.frames_y_btn_up.x,
            self.frames_y_btn_up.x + self.frames_y_btn_up.height,
            BUTTON_WIDTH / 4,
            BUTTON_HEIGHT / 2,
            BUTTON_COLOR,
            text="-",
        )

        def frames_y_btn_down_on_click():
            self.frames_y_btn_model.value = max(self.frames_y_btn_model.value - 1, 1)
            self.frames_y_btn_model.text = f"FRAMES Y: {self.frames_y_btn_model.value}"

        self.frames_y_btn_down.on_click = frames_y_btn_down_on_click

        self.collidable_btn = self.create_button(
            BUTTON_GAP,
            self.get_height() - BUTTON_HEIGHT * 2 - BUTTON_GAP,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            COLLIDABLE_COLOR_OFF_BTN,
            text="COLLIDABLE",
            value=False,
        )

        def collidable_btn_on_click():
            self.collidable_btn.value = not self.collidable_btn.value
            self.collidable_btn.color = COLLIDABLE_COLOR_OFF_BTN
            if self.collidable_btn.value:
                self.collidable_btn.color = COLLIDABLE_COLOR_ON_BTN

        self.collidable_btn.on_click = collidable_btn_on_click

        self.export_btn = self.create_button(
            BUTTON_GAP,
            self.get_height() - BUTTON_HEIGHT - BUTTON_GAP,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            BUTTON_COLOR,
            text="EXPORT",
        )

    def create_button(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        color: Tuple[int, int, int],
        text: Optional[str] = None,
        value: Optional[Any] = None,
    ) -> ButtonModel:
        button = ButtonModel(x, y, width, height, color, text, value)
        self.button_controllers.append(ButtonController(button))
        self.button_views.append(ButtonView(button))
        return button

    def handle_event(self, event: pygame.Event):
        for button_controller in self.button_controllers:
            button_controller.handle_event(event)

    def draw(self):
        self.fill((0, 0, 0))
        for button_view in self.button_views:
            button_view.draw(self)
