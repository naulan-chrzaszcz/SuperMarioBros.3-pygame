from __future__ import annotations

from enum import Enum, auto
from math import sin

import pygame
from pygame import SRCALPHA, Surface, Vector2

from ..constants import BLACK, SAND
from ..inputs.config import Action
from .scene import GameContext, Scene


class AnimationState(Enum):
    PAUSE = auto()
    CURTAIN_UP = auto()
    TITLE_DROP = auto()
    PRESS_A = auto()


class MainMenuScene(Scene):
    """Title screen: the curtain rises, the title drops, then a menu appears.

    Confirming during the opening skips it. In the menu, up and down choose,
    confirm opens the choice and going back quits.
    """

    MENU = ("START GAME", "CUSTOM LEVELS", "MAP EDITOR", "QUIT")
    MENU_TOP = 150
    MENU_SPACING = 12

    duration = {
        AnimationState.PAUSE: 1.0,
        AnimationState.CURTAIN_UP: 2.0,
        AnimationState.TITLE_DROP: 1.0,
    }
    CURTAIN_RAISED = Vector2(0, -171)
    FLOOR_TOP = 203
    TITLE_TOP = 30

    def __init__(self, context: GameContext, play_opening: bool = True):
        super().__init__(context)
        self.play_opening = play_opening
        sheet = context.ressources.image("mainMenu")
        self.curtain = self._repeat(sheet.subsurface((0, 0), (256, 187)))
        self.floor = self._repeat(sheet.subsurface((0, 188), (256, 37)))
        self.small_cloud = sheet.subsurface((180, 285), (16, 8))
        self.cloud = sheet.subsurface((180, 268), (32, 16))
        self.small_cactus = sheet.subsurface((257, 188), (64, 64))
        self.cactus = sheet.subsurface((322, 188), (63, 93))
        self.title = Surface((179, 113), SRCALPHA)
        self.title.blit(sheet.subsurface((0, 226), (179, 72)), (0, 0))
        self.title.blit(sheet.subsurface((180, 226), (42, 41)), (self.title.get_width() // 2 - 20, 72))
        self.menu = [context.font.render(item) for item in self.MENU]
        self.selected = 0

        width = self.surface.get_width()
        title_x = width // 2 - self.title.get_width() // 2
        self.title_start = Vector2(title_x, -self.title.get_height())
        self.title_end = Vector2(title_x, self.TITLE_TOP)

    @staticmethod
    def _repeat(image: Surface) -> Surface:
        """The image twice side by side, wide enough for the whole screen."""
        surface = Surface((image.get_width() * 2, image.get_height()), SRCALPHA)
        surface.blit(image, (0, 0))
        surface.blit(image, (image.get_width(), 0))
        return surface

    def on_enter(self) -> None:
        super().on_enter()
        self.clock = 0.0
        if self.play_opening:
            # Only the first time: coming back from the world map shows the menu.
            self.play_opening = False
            self.state = AnimationState.PAUSE
            self.curtain_pos = Vector2(0, 0)
            self.title_pos = self.title_start.copy()
        else:
            self.skip_opening()

    def skip_opening(self) -> None:
        self.state = AnimationState.PRESS_A
        self.curtain_pos = self.CURTAIN_RAISED.copy()
        self.title_pos = self.title_end.copy()
        self.timer = 0.0

    @property
    def ready(self) -> bool:
        return self.state == AnimationState.PRESS_A

    def on_action(self, action: Action) -> None:
        if action == Action.CONFIRM:
            if self.ready:
                self.choose(self.MENU[self.selected])
            else:
                self.skip_opening()
        elif action == Action.BACK:
            self.manager.quit()
        elif self.ready and action in (Action.UP, Action.DOWN):
            step = -1 if action == Action.UP else 1
            self.selected = (self.selected + step) % len(self.MENU)

    def choose(self, item: str) -> None:
        if item == "START GAME":
            self.manager.change_scene("animation_levels")
        elif item == "CUSTOM LEVELS":
            self.manager.change_scene("custom_levels")
        elif item == "MAP EDITOR":
            self.context.open_editor()
        elif item == "QUIT":
            self.manager.quit()

    def _next_state(self, state: AnimationState) -> None:
        self.state = state
        self.timer = 0.0

    def update(self, dt: float) -> None:
        super().update(dt)
        self.clock += dt
        if self.state == AnimationState.PRESS_A:
            return
        t = min(self.timer / self.duration[self.state], 1.0)
        if self.state == AnimationState.CURTAIN_UP:
            self.curtain_pos = Vector2(0, 0).lerp(self.CURTAIN_RAISED, t)
        elif self.state == AnimationState.TITLE_DROP:
            self.title_pos = self.title_start.lerp(self.title_end, t)
        if t >= 1.0:
            following = list(AnimationState)[list(AnimationState).index(self.state) + 1]
            self._next_state(following)

    def draw(self) -> None:
        width, height = self.surface.get_size()
        curtain_up = self.state not in (AnimationState.PAUSE, AnimationState.CURTAIN_UP)

        self.surface.fill(SAND if curtain_up else BLACK)
        self.surface.blit(self.curtain, self.curtain_pos)
        if curtain_up:
            bob = sin(self.clock / 2)
            self.surface.blit(self.cloud, (width / 3.5 - 22, height / 4 - 12 + bob * 5))
            self.surface.blit(self.small_cloud, (width / 3.5 + 185, height / 4 + 22 + bob * 3.5))
            self.surface.blit(self.small_cactus, (0, height - 101))
            self.surface.blit(self.cactus, (width - 63, height - 130))
        self.surface.blit(self.floor, (0, self.FLOOR_TOP))
        self.surface.blit(self.title, self.title_pos)
        if self.ready:
            self._draw_menu(width)

    def _draw_menu(self, width: int) -> None:
        left = width // 2 - max(item.get_width() for item in self.menu) // 2
        for index, item in enumerate(self.menu):
            y = self.MENU_TOP + index * self.MENU_SPACING
            self.surface.blit(item, (left, y))
            if index == self.selected:
                pygame.draw.polygon(self.surface, BLACK, [(left - 12, y), (left - 12, y + 7), (left - 5, y + 3)])
