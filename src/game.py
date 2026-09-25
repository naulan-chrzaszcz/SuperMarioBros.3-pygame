from __future__ import annotations

from typing import Iterable, Optional, Tuple

import pygame
from pygame import Rect, Surface

from .constants import BLACK, MAX_FRAME_TIME, TITLE
from .font import Font
from .hud import HUD
from .inputs.config import Config
from .inputs.ressources import Ressources
from .inputs.save import Save
from .map_manager import MapManager
from .scene_manager import SceneManager
from .scenes import AnimationLevelsScene, GameContext, IntroScene, LevelsScene, MainMenuScene


def fit(inner: Tuple[int, int], outer: Tuple[int, int], integer: bool = False) -> Rect:
    """Largest rectangle with the proportions of ``inner`` centred in ``outer``."""
    scale = min(outer[0] / inner[0], outer[1] / inner[1])
    if integer and scale >= 1:
        scale = int(scale)
    size = (max(1, int(inner[0] * scale)), max(1, int(inner[1] * scale)))
    return Rect(((outer[0] - size[0]) // 2, (outer[1] - size[1]) // 2), size)


class Game:
    """Composition root: opens the window, loads the files and runs the scenes.

    The game is drawn on a small ``display`` surface (NES-like resolution) that
    is scaled to the window without distorting it.
    """

    def __init__(self, config: Optional[Config] = None, save: Optional[Save] = None):
        self.config = config or Config.load()
        mixer = self.config.mixer
        pygame.mixer.pre_init(mixer.frequency, mixer.size, mixer.channels, mixer.buffer)
        pygame.init()

        screen = self.config.screen
        flags = screen.flags | (pygame.RESIZABLE if screen.resizable else 0)
        self.window = pygame.display.set_mode((screen.width, screen.height), flags, screen.depth)
        pygame.display.set_caption(TITLE)
        pygame.mouse.set_visible(self.config.mouse.visible)

        display = Surface((self.config.display.width, self.config.display.height))
        ressources = Ressources.load()
        save = save or Save.load()
        font = Font(ressources.image("font"))
        self.context = GameContext(
            config=self.config,
            ressources=ressources,
            save=save,
            font=font,
            hud=HUD(ressources.image("hud"), font, save),
            maps=MapManager(ressources),
            display=display,
        )

        self.scenes = SceneManager()
        self.scenes.register("intro", IntroScene(self.context))
        self.scenes.register("main_menu", MainMenuScene(self.context))
        self.scenes.register("animation_levels", AnimationLevelsScene(self.context))
        self.scenes.register("levels", LevelsScene(self.context))
        self.scenes.set_default_scene("main_menu" if self.config.skip_intro else "intro")
        self.clock = pygame.time.Clock()

    @property
    def running(self) -> bool:
        return self.scenes.running

    def step(self, events: Iterable[pygame.event.Event], dt: float) -> None:
        """One frame: events, update, then drawing on the window."""
        self.scenes.handle_events(events)
        if not self.running:
            return
        self.scenes.update(min(dt, MAX_FRAME_TIME))
        self.scenes.draw()
        self.present()

    def present(self) -> None:
        display = self.context.display
        self.window = pygame.display.get_surface()
        area = fit(display.get_size(), self.window.get_size(), self.config.screen.integer_scaling)
        self.window.fill(BLACK)
        self.window.blit(pygame.transform.scale(display, area.size), area)

    def run(self) -> None:
        try:
            while self.running:
                self.step(pygame.event.get(), self.clock.tick(self.config.framerate_limit) / 1000.0)
                pygame.display.flip()
        finally:
            pygame.quit()
