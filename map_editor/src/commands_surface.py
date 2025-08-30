from .constantes import (
    BUTTON_GAP,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
    BUTTON_COLOR,
    FONT_SIZE,
    COLLIDABLE_COLOR_OFF_BTN,
    COLLIDABLE_COLOR_ON_BTN,
)

from .button import Button

import pygame


class CommandsSurface(pygame.Surface):
    def __init__(self, width, height):
        super().__init__((width, height))
        self.font = pygame.font.SysFont("Arial", FONT_SIZE)
        self.rotation_btn = Button(
            BUTTON_GAP, BUTTON_GAP, BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_COLOR
        )
        self.rotation_btn.value = 0
        self.rotation_btn.text = f"ROTATION: {self.rotation_btn.value}"

        def rotation_btn_on_click():
            self.rotation_btn.value += 90
            self.rotation_btn.value %= 360
            self.rotation_btn.text = f"ROTATION: {self.rotation_btn.value}"

        self.rotation_btn.on_click = rotation_btn_on_click

        self.frames_x_btn = Button(
            self.rotation_btn.x,
            self.rotation_btn.y + BUTTON_HEIGHT + BUTTON_GAP,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            BUTTON_COLOR,
        )
        self.frames_x_btn.value = 1
        self.frames_x_btn.text = f"FRAMES X: {self.frames_x_btn.value}"

        self.frames_x_btn_up = Button(
            self.frames_x_btn.x + self.frames_x_btn.width + BUTTON_GAP,
            self.rotation_btn.y + BUTTON_HEIGHT + BUTTON_GAP,
            BUTTON_WIDTH / 4,
            BUTTON_HEIGHT / 2,
            BUTTON_COLOR,
        )
        self.frames_x_btn_up.text = "+"

        def frames_x_btn_up_on_click():
            self.frames_x_btn.value += 1
            self.frames_x_btn.text = f"FRAMES X: {self.frames_x_btn.value}"

        self.frames_x_btn_up.on_click = frames_x_btn_up_on_click

        self.frames_x_btn_down = Button(
            self.frames_x_btn.x + self.frames_x_btn.width + BUTTON_GAP,
            self.frames_x_btn_up.bottom,
            BUTTON_WIDTH / 4,
            BUTTON_HEIGHT / 2,
            BUTTON_COLOR,
        )
        self.frames_x_btn_down.text = "-"

        def frames_x_btn_down_on_click():
            self.frames_x_btn.value = max(self.frames_x_btn.value - 1, 1)
            self.frames_x_btn.text = f"FRAMES X: {self.frames_x_btn.value}"

        self.frames_x_btn_down.on_click = frames_x_btn_down_on_click

        self.frames_y_btn = Button(
            self.frames_x_btn.x,
            self.frames_x_btn_down.y + BUTTON_HEIGHT / 2 + BUTTON_GAP,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            BUTTON_COLOR,
        )
        self.frames_y_btn.value = 1
        self.frames_y_btn.text = f"FRAMES Y: {self.frames_y_btn.value}"

        self.frames_y_btn_up = Button(
            self.frames_x_btn_down.x,
            self.frames_x_btn_down.bottom + BUTTON_GAP,
            BUTTON_WIDTH / 4,
            BUTTON_HEIGHT / 2,
            BUTTON_COLOR,
        )
        self.frames_y_btn_up.text = "+"

        def frames_y_btn_up_on_click():
            self.frames_y_btn.value += 1
            self.frames_y_btn.text = f"FRAMES Y: {self.frames_y_btn.value}"

        self.frames_y_btn_up.on_click = frames_y_btn_up_on_click

        self.frames_y_btn_down = Button(
            self.frames_y_btn_up.x,
            self.frames_y_btn_up.bottom,
            BUTTON_WIDTH / 4,
            BUTTON_HEIGHT / 2,
            BUTTON_COLOR,
        )
        self.frames_y_btn_down.text = "-"

        def frames_y_btn_down_on_click():
            self.frames_y_btn.value = max(self.frames_y_btn.value - 1, 1)
            self.frames_y_btn.text = f"FRAMES Y: {self.frames_y_btn.value}"

        self.frames_y_btn_down.on_click = frames_y_btn_down_on_click

        self.collidable_btn = Button(
            BUTTON_GAP,
            self.get_height() - BUTTON_HEIGHT - BUTTON_GAP,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            COLLIDABLE_COLOR_OFF_BTN,
        )
        self.collidable_btn.text = "COLLIDABLE"
        self.collidable_btn.value = False

        def collidable_btn_on_click():
            self.collidable_btn.value = not self.collidable_btn.value
            self.collidable_btn.color = COLLIDABLE_COLOR_OFF_BTN
            if self.collidable_btn.value:
                self.collidable_btn.color = COLLIDABLE_COLOR_ON_BTN

        self.collidable_btn.on_click = collidable_btn_on_click

        self.export_btn = Button(
            BUTTON_GAP,
            self.get_height() - BUTTON_HEIGHT - BUTTON_GAP,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            BUTTON_COLOR,
        )
        self.export_btn.text = "EXPORT"

    def handle_event(self, event: pygame.Event):
        self.rotation_btn.handle_event(event)
        self.frames_x_btn_up.handle_event(event)
        self.frames_x_btn_down.handle_event(event)
        self.frames_y_btn_up.handle_event(event)
        self.frames_y_btn_down.handle_event(event)
        self.collidable_btn.handle_event(event)
        self.export_btn.handle_event(event)

    def draw(self):
        self.fill((0, 0, 0))
        self.rotation_btn.draw(self)
        self.frames_x_btn.draw(self)
        self.frames_x_btn_up.draw(self)
        self.frames_x_btn_down.draw(self)
        self.frames_y_btn.draw(self)
        self.frames_y_btn_up.draw(self)
        self.frames_y_btn_down.draw(self)
        self.collidable_btn.draw(self)
        self.export_btn.draw(self)
