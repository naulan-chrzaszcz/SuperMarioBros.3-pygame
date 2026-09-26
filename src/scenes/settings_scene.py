"""SETTINGS: changes ``config.yaml`` from the game, without editing the file.

Every row is an :class:`Option`: it reads a value in the :class:`Config` and
gives back a new one, so adding a setting to the screen is one line in
``OPTIONS``. Leaving the screen writes ``config.yaml``.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable, List, Optional, Tuple

import pygame
from pygame import KEYDOWN

from ..constants import BLACK, WHITE
from ..inputs.config import Action, Config, Controls
from .scene import GameContext, Scene

MUTED = (140, 140, 140)
# Keys a binding must not steal: the game would become impossible to leave.
RESERVED = ("escape",)


@dataclass(frozen=True)
class Option:
    """A row of the screen: a label, the value it shows and how to change it."""

    label: str
    show: Callable[[Config], str]
    change: Callable[[Config, int], Config]


def _volume(name: str) -> Option:
    def show(config: Config) -> str:
        # The font has no "%": the number alone is clear enough (0 to 100).
        return str(round(getattr(config.audio, name) * 100))

    def change(config: Config, step: int) -> Config:
        volume = min(1.0, max(0.0, round(getattr(config.audio, name) + step * 0.1, 2)))
        return replace(config, audio=replace(config.audio, **{name: volume}))

    return Option(name.replace("_", " ").upper(), show, change)


def _switch(label: str, section: Optional[str], name: str) -> Option:
    """A setting that is on or off."""

    def owner(config: Config):
        return config if section is None else getattr(config, section)

    def show(config: Config) -> str:
        return "ON" if getattr(owner(config), name) else "OFF"

    def change(config: Config, step: int) -> Config:
        value = not getattr(owner(config), name)
        if section is None:
            return replace(config, **{name: value})
        return replace(config, **{section: replace(owner(config), **{name: value})})

    return Option(label, show, change)


def _framerate(choices: Tuple[int, ...] = (30, 60, 120, 240)) -> Option:
    def show(config: Config) -> str:
        return str(config.framerate_limit)

    def change(config: Config, step: int) -> Config:
        if config.framerate_limit in choices:
            index = choices.index(config.framerate_limit) + step
        else:
            index = 0
        return replace(config, framerate_limit=choices[index % len(choices)])

    return Option("FRAMERATE", show, change)


OPTIONS: Tuple[Option, ...] = (
    _switch("AUDIO", "audio", "enabled"),
    _volume("music_volume"),
    _volume("sound_volume"),
    _switch("SHARP PIXELS", "screen", "integer_scaling"),
    _switch("SKIP INTRO", None, "skip_intro"),
    _switch("MOUSE CURSOR", "mouse", "visible"),
    _framerate(),
)


class SettingsScene(Scene):
    """Changes the settings of the game and saves them.

    Up and down choose a row, left and right change it. The last rows open the
    controls (confirm a line, then press the key it should use) and put the
    default settings back. Going back saves ``config.yaml`` and returns to the
    title screen.
    """

    NAME = "settings"
    ROW_HEIGHT = 13
    LIST_TOP = 40
    CONTROLS_ROW = len(OPTIONS)
    DEFAULTS_ROW = len(OPTIONS) + 1
    ROWS = len(OPTIONS) + 2

    def __init__(self, context: GameContext):
        super().__init__(context)
        self.selected = 0
        # False: the list of the settings; True: the page of the controls.
        self.controls = False
        self.waiting = False
        self.message: Optional[str] = None

    @property
    def config(self) -> Config:
        return self.context.config

    @property
    def actions(self) -> List[Action]:
        return list(self.config.controls.bindings)

    def on_enter(self) -> None:
        super().on_enter()
        self.selected = 0
        self.controls = False
        self.waiting = False
        self.message = None

    def handle_event(self, event) -> None:
        """While waiting for a key, every key is a binding, not an action."""
        if self.waiting and event.type == KEYDOWN:
            self.bind(pygame.key.name(event.key).lower())
            return
        super().handle_event(event)

    def on_action(self, action: Action) -> None:
        if action in (Action.UP, Action.DOWN):
            self.move(-1 if action == Action.UP else 1)
        elif action in (Action.LEFT, Action.RIGHT):
            self.change(-1 if action == Action.LEFT else 1)
        elif action == Action.CONFIRM:
            self.confirm()
        elif action == Action.BACK:
            self.back()

    def move(self, step: int) -> None:
        rows = len(self.actions) if self.controls else self.ROWS
        self.selected = (self.selected + step) % rows
        self.message = None
        self.context.audio.play("menu_select")

    def change(self, step: int) -> None:
        if self.controls or self.selected >= len(OPTIONS):
            return
        self.apply(OPTIONS[self.selected].change(self.config, step))
        self.context.audio.play("menu_select")

    def confirm(self) -> None:
        self.context.audio.play("menu_confirm")
        if self.controls:
            self.waiting = True
            self.message = "PRESS A KEY   ESC CANCEL"
        elif self.selected == self.CONTROLS_ROW:
            self.controls = True
            self.selected = 0
            self.message = None
        elif self.selected == self.DEFAULTS_ROW:
            self.apply(Config())
            self.message = "DEFAULT SETTINGS"
        else:
            self.change(1)

    def bind(self, key_name: str) -> None:
        """The key the player pressed becomes the key of the chosen action."""
        self.waiting = False
        if key_name in RESERVED:
            self.message = None
            return
        action = self.actions[self.selected]
        bindings = {
            name: tuple(key for key in keys if key != key_name) or keys
            for name, keys in self.config.controls.bindings.items()
        }
        bindings[action] = (key_name,)
        controls = Controls(bindings)
        self.apply(replace(self.config, controls=controls))
        self.message = None

    def apply(self, config: Config) -> None:
        """Uses the new settings right away (the game also writes them)."""
        self.context.apply_config(config)

    def back(self) -> None:
        if self.waiting:
            self.waiting = False
            self.message = None
        elif self.controls:
            self.controls = False
            self.selected = self.CONTROLS_ROW
            self.message = None
        else:
            self.context.save_config()
            self.manager.change_scene("main_menu")

    def draw(self) -> None:
        surface = self.surface
        font = self.context.font
        width, height = surface.get_size()
        surface.fill(BLACK)
        pygame.draw.rect(surface, WHITE, surface.get_rect().inflate(-16, -16), 1)

        title = font.render("CONTROLS" if self.controls else "SETTINGS")
        surface.blit(title, (width // 2 - title.get_width() // 2, 20))

        left = 48
        for index, (label, value) in enumerate(self.rows()):
            y = self.LIST_TOP + index * self.ROW_HEIGHT
            surface.blit(font.render(label), (left, y))
            if value:
                image = font.render(value)
                surface.blit(image, (width - left - image.get_width(), y))
            if index == self.selected:
                arrow = [(left - 14, y), (left - 14, y + 7), (left - 7, y + 3)]
                pygame.draw.polygon(surface, WHITE, arrow)

        footer = self.message or self.hint
        for index, line in enumerate(font.wrap(footer, 52)[-2:]):
            image = font.render(line)
            surface.blit(image, (width // 2 - image.get_width() // 2, height - 40 + index * 11))

    @property
    def hint(self) -> str:
        if self.controls:
            return "A CHANGE KEY   ESC BACK"
        return "ARROWS CHANGE   ESC SAVE AND BACK"

    def rows(self) -> List[Tuple[str, str]]:
        """The lines to draw: the settings, or the controls."""
        if self.controls:
            return [
                (action.name, " ".join(keys).upper())
                for action, keys in self.config.controls.bindings.items()
            ]
        rows = [(option.label, option.show(self.config)) for option in OPTIONS]
        rows.append(("CONTROLS", ""))
        rows.append(("DEFAULT SETTINGS", ""))
        return rows
