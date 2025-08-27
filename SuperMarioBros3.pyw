"""
"Fan Game" created by CHRZASZCZ Naulan.
    * Created the 26/09/2020 at 8:35am.
"""

import pygame

from src.inputs.ressources import Ressources
from src.inputs.map import Map
from src.map_manager import MapManager
from src.display import Display
from src.scene_manager import SceneManager
from src.inputs.config import Config
from src.scenes import (
    AnimationLevelsScene,
    MainMenuScene,
    AnimationMainMenuScene,
    IntroScene,
)

config = Config()
pygame.mixer.init(
    config.mixer.frequency,
    config.mixer.size,
    config.mixer.channels,
    config.mixer.buffer,
)
pygame.init()

screen = pygame.display.set_mode(
    (config.screen.width, config.screen.height),
    config.screen.flags,
    config.screen.depth,
)
pygame.mouse.set_visible(config.mouse.visible)

scene_manager = SceneManager()
scene_manager.register("intro", IntroScene())
scene_manager.register("animation_main_menu", AnimationMainMenuScene())
scene_manager.register("main_menu", MainMenuScene())
scene_manager.register("animation_levels", AnimationLevelsScene())
scene_manager.set_default_scene("animation_main_menu" if config.skip_intro else "intro")

map_manager = MapManager()
map_manager.register(
    "levels", Map(Ressources()["images"]["levels"], Ressources()["metadata"]["levels"], Ressources()["maps"]["levels"])
)

display = Display()
clock = pygame.time.Clock()
while True:
    scene_manager.handle_events(pygame.event.get())
    screen.fill((0, 0, 0))
    scene_manager.draw()
    screen.blit(pygame.transform.scale(display, screen.get_size()), (0, 0))

    scene_manager.update(clock.tick(config.framerate_limit) / 1000.0)
    pygame.display.update()
