from math import sin
from pygame import SRCALPHA, Surface, KEYDOWN, K_a

from ..inputs.ressources import Ressources
from ..font import Font
from .scene import Scene


class MainMenuScene(Scene):
    def __init__(self):
        super().__init__()
        sheet = Ressources()["images"]["mainMenu"]
        self.shadow_curtain = sheet.subsurface((257, 0), (256, 187))
        self.curtain = Surface((512, 187), SRCALPHA)
        self.curtain.blit(sheet.subsurface((0, 0), (256, 187)), (0, 0))
        self.curtain.blit(sheet.subsurface((0, 0), (256, 187)), (256, 0))
        self.floor = Surface((512, 37))
        self.floor.blit(sheet.subsurface((0, 188), (256, 37)), (0, 0))
        self.floor.blit(sheet.subsurface((0, 188), (256, 37)), (256, 0))
        self.small_cloud = sheet.subsurface((180, 285), (16, 8))
        self.cloud = sheet.subsurface((180, 268), (32, 16))
        self.small_cactus = sheet.subsurface((257, 188), (64, 64))
        self.cactus = sheet.subsurface((322, 188), (63, 93))
        self.title = Surface((179, 113), SRCALPHA)
        self.title.blit(sheet.subsurface((0, 226), (179, 72)), (0, 0))
        self.title.blit(
            sheet.subsurface((180, 226), (42, 41)),
            (self.title.get_width() / 2 - 20.5, 72),
        )
        self.subtitle = Font().render("PRESS A TO START")

    def handle_event(self, event):
        if event.type == KEYDOWN:
            if event.key == K_a:
                self.manager.change_scene("animation_levels")

    def update(self, dt):
        self.timer += dt

    def draw(self):
        w = self.surface.get_width()
        h = self.surface.get_height()

        self.surface.fill((255, 219, 161))
        self.surface.blit(self.curtain, (0, -171))
        self.surface.blit(
            self.cloud, (w / 3.5 - 22, (h / 4 - 12) + sin(self.timer / 2) * 5)
        )
        self.surface.blit(
            self.small_cloud, (w / 3.5 + 185, (h / 4 + 22) + sin(self.timer / 2) * 3.5)
        )
        self.surface.blit(self.small_cactus, (0, h - 101))
        self.surface.blit(self.cactus, (w - 63, h - 130))
        self.surface.blit(self.floor, (0, 203))
        self.surface.blit(
            self.title,
            (
                self.surface.get_width() / 2 - self.title.get_width() / 2,
                self.surface.get_height() / 2 - self.title.get_width() / 2,
            ),
        )
        self.surface.blit(
            self.subtitle,
            (w / 2 - self.subtitle.get_width() / 2, h / 4 + self.title.get_height()),
        )
