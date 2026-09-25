from typing import Any, Optional, Tuple

import pygame

from .constantes import (
    BUTTON_COLOR,
    BUTTON_GAP,
    BUTTON_HEIGHT,
    BUTTON_WIDTH,
    COLLIDABLE_COLOR_OFF_BTN,
    COLLIDABLE_COLOR_ON_BTN,
    FONT_SIZE,
)
from .controllers import ButtonController
from .models import ButtonModel
from .views import ButtonView


class CommandsSurface(pygame.Surface):
    def __init__(self, width: int, height: int) -> None:
        super().__init__((width, height))
        self.font = pygame.font.SysFont("Arial", FONT_SIZE)
        self.button_controllers = []
        self.button_views = []
        self.max_frames_x = 1
        self.max_frames_y = 1

        self.rotation_btn_model = self.create_button(
            BUTTON_GAP,
            BUTTON_GAP,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            BUTTON_COLOR,
            text="ROTATION: 0",
            value=0,
        )
        self.rotation_btn_model.on_click = self.rotate

        self.frames_x_btn_model = self.create_button(
            BUTTON_GAP,
            BUTTON_GAP * 2 + BUTTON_HEIGHT,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            BUTTON_COLOR,
            text="FRAMES X: 1",
            value=1,
        )
        self.frames_x_btn_up_model = self.create_button(
            self.frames_x_btn_model.x + BUTTON_WIDTH + BUTTON_GAP,
            self.frames_x_btn_model.y,
            BUTTON_WIDTH // 4,
            BUTTON_HEIGHT // 2,
            BUTTON_COLOR,
            text="+",
        )
        self.frames_x_btn_up_model.on_click = self.increase_frames_x
        self.frames_x_btn_down_model = self.create_button(
            self.frames_x_btn_up_model.x,
            self.frames_x_btn_up_model.y + self.frames_x_btn_up_model.height,
            BUTTON_WIDTH // 4,
            BUTTON_HEIGHT // 2,
            BUTTON_COLOR,
            text="-",
        )
        self.frames_x_btn_down_model.on_click = self.decrease_frames_x

        self.frames_y_btn_model = self.create_button(
            BUTTON_GAP,
            BUTTON_GAP * 3 + BUTTON_HEIGHT * 2,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            BUTTON_COLOR,
            text="FRAMES Y: 1",
            value=1,
        )
        self.frames_y_btn_up_model = self.create_button(
            self.frames_y_btn_model.x + BUTTON_WIDTH + BUTTON_GAP,
            self.frames_y_btn_model.y,
            BUTTON_WIDTH // 4,
            BUTTON_HEIGHT // 2,
            BUTTON_COLOR,
            text="+",
        )
        self.frames_y_btn_up_model.on_click = self.increase_frames_y
        self.frames_y_btn_down_model = self.create_button(
            self.frames_y_btn_up_model.x,
            self.frames_y_btn_up_model.y + self.frames_y_btn_up_model.height,
            BUTTON_WIDTH // 4,
            BUTTON_HEIGHT // 2,
            BUTTON_COLOR,
            text="-",
        )
        self.frames_y_btn_down_model.on_click = self.decrease_frames_y

        self.collidable_btn = self.create_button(
            BUTTON_GAP,
            self.get_height() - BUTTON_HEIGHT * 2 - BUTTON_GAP,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            COLLIDABLE_COLOR_OFF_BTN,
            text="COLLIDABLE",
            value=False,
        )
        self.collidable_btn.on_click = self.toggle_collidable

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

    def rotate(self) -> None:
        self.rotation_btn_model.value = (self.rotation_btn_model.value + 90) % 360
        self.rotation_btn_model.text = f"ROTATION: {self.rotation_btn_model.value}"

    def increase_frames_x(self) -> None:
        self.frames_x_btn_model.value = min(
            self.frames_x_btn_model.value + 1, self.max_frames_x
        )
        if self.frames_x_btn_model.value > 1:
            self.frames_y_btn_model.value = 1
        self._update_frame_labels()

    def decrease_frames_x(self) -> None:
        self.frames_x_btn_model.value = max(self.frames_x_btn_model.value - 1, 1)
        self._update_frame_labels()

    def increase_frames_y(self) -> None:
        self.frames_y_btn_model.value = min(
            self.frames_y_btn_model.value + 1, self.max_frames_y
        )
        if self.frames_y_btn_model.value > 1:
            self.frames_x_btn_model.value = 1
        self._update_frame_labels()

    def decrease_frames_y(self) -> None:
        self.frames_y_btn_model.value = max(self.frames_y_btn_model.value - 1, 1)
        self._update_frame_labels()

    def toggle_collidable(self) -> None:
        self.collidable_btn.value = not self.collidable_btn.value
        self.collidable_btn.color = (
            COLLIDABLE_COLOR_ON_BTN
            if self.collidable_btn.value
            else COLLIDABLE_COLOR_OFF_BTN
        )

    def set_frame_limits(self, max_frames_x: int, max_frames_y: int) -> None:
        self.max_frames_x = max(1, max_frames_x)
        self.max_frames_y = max(1, max_frames_y)
        self.frames_x_btn_model.value = min(
            self.frames_x_btn_model.value, self.max_frames_x
        )
        self.frames_y_btn_model.value = min(
            self.frames_y_btn_model.value, self.max_frames_y
        )
        self._update_frame_labels()

    def handle_event(self, event: pygame.event.Event) -> None:
        for button_controller in self.button_controllers:
            button_controller.handle_event(event)

    def draw(self) -> None:
        self.fill((0, 0, 0))
        for button_view in self.button_views:
            button_view.draw(self)

    def _update_frame_labels(self) -> None:
        self.frames_x_btn_model.text = f"FRAMES X: {self.frames_x_btn_model.value}"
        self.frames_y_btn_model.text = f"FRAMES Y: {self.frames_y_btn_model.value}"
