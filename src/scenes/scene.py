"""Base class of the scenes and the ``GameContext`` they share.

A scene gets ``on_enter`` / ``on_exit`` when it becomes (or stops being) the
current one, then ``update``, ``draw`` and ``on_action`` every frame.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Optional

from pygame import KEYDOWN, KEYUP, Surface, key

from ..animation import SpriteBank
from ..audio import Audio
from ..font import Font
from ..hud import HUD
from ..inputs.config import Action, Config
from ..inputs.ressources import Ressources
from ..inputs.rules import Rules
from ..inputs.save import Save
from ..map_manager import MapManager

if TYPE_CHECKING:
    from ..levels import LevelCatalog, LevelInfo

PlayLevel = Callable[["LevelInfo", Callable[[bool], None]], None]


def _unavailable(*_args, **_kwargs) -> None:
    raise RuntimeError("Not available outside of the game")


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
    levels: Optional["LevelCatalog"] = None
    # res/rules.yaml, res/sprites.yaml and the sounds of ressources.yaml.
    rules: Rules = field(default_factory=Rules)
    sprites: Optional[SpriteBank] = None
    audio: Audio = field(default_factory=lambda: Audio({}, {}))
    # Opens the map editor in the game window (after the current frame).
    open_editor: Callable[[], None] = field(default=_unavailable)
    # play_level(level, on_finish): plays a map, then calls on_finish(cleared).
    play_level: PlayLevel = field(default=_unavailable)
    # Uses new settings right away, then writes them to config.yaml.
    apply_config: Callable[[Config], None] = field(default=_unavailable)
    save_config: Callable[[], None] = field(default=_unavailable)
    persist_progress: Callable[[], None] = field(default=_unavailable)

    def __post_init__(self) -> None:
        if self.sprites is None:
            self.sprites = SpriteBank(self.ressources)


class Scene:
    """A screen of the game (title, world map, level...).

    Lifecycle: ``on_enter`` when it becomes the current scene, then every frame
    ``handle_event`` (which calls ``on_action`` / ``on_action_released``),
    ``update(dt)`` and ``draw()``; ``on_exit`` when another scene replaces it.
    Switch scene with ``self.manager.change_scene(name)``.
    """

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
        """An action of ``config.yaml`` was pressed."""

    def on_action_released(self, action: Action) -> None:
        """An action of ``config.yaml`` was released."""

    def update(self, dt: float) -> None:
        """Moves the scene on by ``dt`` seconds; ``self.timer`` counts from ``on_enter``."""
        self.timer += dt

    def draw(self) -> None:
        """Draws the scene on ``self.surface`` (the game image, scaled to the window)."""

    def on_enter(self) -> None:
        """Called each time the scene starts: reset its state here."""
        self.timer = 0.0

    def on_exit(self) -> None:
        """Called when another scene replaces this one."""
