from __future__ import annotations

from typing import Iterable, Optional, Tuple

import pygame
from pygame import Rect, Surface

from .animation import SpriteBank
from .audio import Audio
from .constants import BLACK, MAX_FRAME_TIME, TITLE
from .editor_bridge import EditorResult, EditorSession
from .font import Font
from .hud import HUD
from .entities.catalog import entity_types
from .entities.spawner import validate_entity_types
from .inputs.config import Config
from .inputs.ressources import Ressources
from .inputs.rules import Rules
from .inputs.save import Save
from .inputs.tuning import check
from .levels import LevelCatalog, LevelInfo
from .map_manager import MapManager
from .platformer import Body
from .scene_manager import SceneManager
from .scenes import (
    AnimationLevelsScene,
    CustomLevelsScene,
    GameContext,
    IntroScene,
    LevelsScene,
    MainMenuScene,
    PlatformLevelScene,
)


def fit(inner: Tuple[int, int], outer: Tuple[int, int], integer: bool = False) -> Rect:
    """Largest rectangle with the proportions of ``inner`` centred in ``outer``."""
    scale = min(outer[0] / inner[0], outer[1] / inner[1])
    if integer and scale >= 1:
        scale = int(scale)
    size = (max(1, int(inner[0] * scale)), max(1, int(inner[1] * scale)))
    return Rect(((outer[0] - size[0]) // 2, (outer[1] - size[1]) // 2), size)


def validate_data(rules: Rules, sprites: SpriteBank, ressources: Ressources) -> None:
    """Checks the data files when the game starts, so that a typo in them
    is reported at once rather than in the middle of a level."""
    check(Body, rules.player, "rules.yaml: player")
    for where, cls, settings in (
        ("level", PlatformLevelScene, rules.level),
        ("worldMap", LevelsScene, rules.world_map),
    ):
        music = check(cls, settings, f"rules.yaml: {where}").get("MUSIC", cls.MUSIC)
        if ressources.musics and music not in ressources.musics:
            known = ", ".join(ressources.musics)
            raise ValueError(f"rules.yaml: {where}: unknown music {music!r} (known: {known})")
    validate_entity_types(entity_types())
    for name in sprites.specs:
        sprites.animations(name)
    for name in entity_types().values():
        if name.behaviour != "start":
            sprites.build(name.image, name.animations, name.facing, name.palette, name.id)


class Game:
    """Composition root: opens the window, loads the files and runs the scenes.

    The game is drawn on a small ``display`` surface (NES-like resolution) that
    is scaled to the window without distorting it.
    """

    def __init__(
        self,
        config: Optional[Config] = None,
        save: Optional[Save] = None,
        levels: Optional[LevelCatalog] = None,
        editor: Optional[EditorSession] = None,
        rules: Optional[Rules] = None,
    ):
        self.config = config or Config.load()
        mixer = self.config.mixer
        pygame.mixer.pre_init(mixer.frequency, mixer.size, mixer.channels, mixer.buffer)
        pygame.init()

        screen = self.config.screen
        self.open_window((screen.width, screen.height))

        display = Surface((self.config.display.width, self.config.display.height))
        ressources = Ressources.load()
        save = save or Save.load()
        font = Font(ressources.image("font"))
        rules = rules or Rules.load()
        sprites = SpriteBank(ressources)
        validate_data(rules, sprites, ressources)
        if levels is None:
            # The world maps of ressources.yaml are not levels.
            levels = LevelCatalog(excluded=[entry["path"] for entry in ressources.maps.values()])
        levels.refresh()
        self.context = GameContext(
            config=self.config,
            ressources=ressources,
            save=save,
            font=font,
            hud=HUD(sprites, font, save),
            maps=MapManager(ressources),
            display=display,
            levels=levels,
            rules=rules,
            sprites=sprites,
            audio=Audio(ressources.sounds, ressources.musics, self.config.audio),
            open_editor=self.open_editor,
            play_level=self.play_level,
        )
        self.editor = editor or EditorSession()
        self._editor_requested = False
        self._editor_origin = "main_menu"

        self.scenes = SceneManager()
        self.scenes.register("intro", IntroScene(self.context))
        self.scenes.register("main_menu", MainMenuScene(self.context))
        self.scenes.register("animation_levels", AnimationLevelsScene(self.context))
        self.scenes.register("levels", LevelsScene(self.context))
        self.scenes.register("custom_levels", CustomLevelsScene(self.context))
        self.level_scene = PlatformLevelScene(self.context)
        self.scenes.register(PlatformLevelScene.NAME, self.level_scene)
        self.scenes.set_default_scene("main_menu" if self.config.skip_intro else "intro")
        self.clock = pygame.time.Clock()

    def open_window(self, size: Tuple[int, int]) -> None:
        screen = self.config.screen
        flags = screen.flags | (pygame.RESIZABLE if screen.resizable else 0)
        self.window = pygame.display.set_mode(size, flags, screen.depth)
        pygame.display.set_caption(TITLE)
        pygame.mouse.set_visible(self.config.mouse.visible)

    @property
    def running(self) -> bool:
        return self.scenes.running

    def step(self, events: Iterable[pygame.event.Event], dt: float) -> None:
        """One frame: events, update, then drawing on the window."""
        self.scenes.handle_events(events)
        if not self.running:
            return
        self.scenes.update(min(dt, MAX_FRAME_TIME))
        if self._editor_requested:
            self._editor_requested = False
            self.run_editor()
            if not self.running:
                return
        self.scenes.draw()
        self.present()

    def open_editor(self) -> None:
        """Asks for the map editor; it opens once the current frame is updated."""
        if not self.editor.paused:
            self._editor_origin = self.scenes.current_name or "main_menu"
        self._editor_requested = True

    def play_level(self, level: LevelInfo, on_finish, practice: bool = False) -> None:
        self.level_scene.start(level, on_finish, practice)

    def run_editor(self) -> EditorResult:
        """Runs the editor in the window, then plays the map it asks for."""
        window_size = self.window.get_size()
        music = self.context.audio.music
        self.context.audio.stop_music()
        result = self.editor.run()
        if result.quit:
            self.scenes.quit()
            return result
        self.open_window(window_size)
        self.context.levels.refresh()
        if result.play:
            level = self.context.levels.info(result.map_path, result.sheet_path)
            # Practice mode: leaving or clearing the level goes back to the editor.
            self.play_level(level, lambda cleared: self.open_editor(), practice=True)
        elif self.scenes.current_name != self._editor_origin:
            self.scenes.change_scene(self._editor_origin)
        else:
            # Same scene: its on_enter is not called again, so its music is resumed here.
            self.context.audio.play_music(music)
        return result

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
