from __future__ import annotations

from dataclasses import dataclass

from pygame import KEYDOWN, KEYUP, Surface, key

from ..font import Font
from ..hud import HUD
from ..inputs.config import Action, Config
from ..inputs.ressources import Ressources
from ..inputs.save import Save
from ..map_manager import MapManager


@dataclass
class GameContext:
    """Everything scenes share, given to them instead of global singletons."""

    config: Config
    ressources: Ressources
    save: Save
    font: Font
    hud: HUD
    maps: MapManager
    display: Surface


class Scene:
    def __init__(self, context: GameContext):
        self.context = context
        self.surface = context.display
        self.manager = None  # set by SceneManager.register
        self.timer = 0.0

    def handle_event(self, event) -> None:
        """Translates key presses into the actions of ``config.yaml``."""
        if event.type not in (KEYDOWN, KEYUP):
            return
        action = self.context.config.controls.action_of(key.name(event.key))
        if action is None:
            return
        if event.type == KEYDOWN:
            self.on_action(action)
        else:
            self.on_action_released(action)

    def on_action(self, action: Action) -> None:
        pass

    def on_action_released(self, action: Action) -> None:
        pass

    def update(self, dt: float) -> None:
        self.timer += dt

    def draw(self) -> None:
        pass

    def on_enter(self) -> None:
        """Called each time the scene starts: reset its state here."""
        self.timer = 0.0

    def on_exit(self) -> None:
        pass
