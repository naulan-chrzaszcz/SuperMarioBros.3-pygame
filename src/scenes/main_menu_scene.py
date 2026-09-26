"""Title screen and its menu: play, custom levels, map editor, settings, quit."""

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

    MENU = ("START GAME", "CUSTOM LEVELS", "MAP EDITOR", "SETTINGS", "QUIT")
    MENU_TOP = 150
    MENU_SPACING = 12
    MUSIC = "title"

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
        # The pictures are the "title" sprite of res/sprites.yaml.

        def picture(name: str) -> Surface:
            return context.sprites.image("title", name)

        self.curtain = self._repeat(picture("curtain"))
        self.floor = self._repeat(picture("floor"))
        self.small_cloud = picture("small_cloud")
        self.cloud = picture("cloud")
        self.small_cactus = picture("small_cactus")
        self.cactus = picture("cactus")
        logo, three = picture("logo"), picture("logo_three")
        size = max(logo.get_width(), three.get_width()), logo.get_height() + three.get_height()
        self.title = Surface(size, SRCALPHA)
        self.title.blit(logo, (0, 0))
        self.title.blit(three, (self.title.get_width() // 2 - three.get_width() // 2 + 1, logo.get_height()))
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
        self.context.audio.play_music(self.MUSIC)
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
                self.context.audio.play("menu_confirm")
                self.choose(self.MENU[self.selected])
            else:
                self.skip_opening()
        elif action == Action.BACK:
            self.manager.quit()
        elif self.ready and action in (Action.UP, Action.DOWN):
            step = -1 if action == Action.UP else 1
            self.selected = (self.selected + step) % len(self.MENU)
            self.context.audio.play("menu_select")

    def choose(self, item: str) -> None:
        if item == "START GAME":
            self.manager.change_scene("animation_levels")
        elif item == "CUSTOM LEVELS":
            self.manager.change_scene("custom_levels")
        elif item == "MAP EDITOR":
            self.context.open_editor()
        elif item == "SETTINGS":
            self.manager.change_scene("settings")
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
                arrow = [(left - 12, y), (left - 12, y + 7), (left - 5, y + 3)]
                pygame.draw.polygon(self.surface, BLACK, arrow)
