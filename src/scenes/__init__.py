"""The scenes of the game. Each one receives a ``GameContext`` and reacts to
actions; ``src/game.py`` registers them by name.
"""

from .animation_levels_scene import AnimationLevelsScene
from .custom_levels_scene import CustomLevelsScene
from .intro_scene import IntroScene
from .levels_scene import LevelsScene
from .main_menu_scene import MainMenuScene
from .platform_level_scene import PlatformLevelScene
from .scene import GameContext, Scene

__all__ = [
    "AnimationLevelsScene",
    "CustomLevelsScene",
    "GameContext",
    "IntroScene",
    "LevelsScene",
    "MainMenuScene",
    "PlatformLevelScene",
    "Scene",
]
