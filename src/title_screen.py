from pygame import Surface
from pygame.locals import *

from src.scenes.scene_1 import Scene1


class TitleScreen(Scene1):
    sheet: Surface

    def __init__(self, sheet):
        super().__init__()
        self.sheet = sheet

        self.color = (0, 0, 0)
        self.keys = None

        self.pass_stage_menu = False; self.is_title = True
        self.dt = .0

    def getIsTitle(self) -> bool:
        return self.is_title

    def getPassStageMenu(self) -> bool:
        return self.pass_stage_menu

    def draw(self, surface) -> None:
        surface.fill(self.getBackgroundColor())

        if not self.getFinish():
            self.start(surface, self.dt)
        else:
            self.t[3] += (.05 * self.dt)
        # Curtain
        surface.blit(self.sheet.subsurface((0,0),(256,35)),(0,-2 - self.curtain_y))
        surface.blit(self.sheet.subsurface((0,0),(256,35)),(256,-2 - self.curtain_y))
        surface.blit(self.sheet.subsurface((0,0),(256,187)),(0,(surface.get_height() - 221) - self.curtain_y))
        surface.blit(self.sheet.subsurface((0,0),(256,187)),(256,(surface.get_height() - 221) - self.curtain_y))
        # Floor
        surface.blit(self.sheet.subsurface((0,188),(256,37)),(0,surface.get_height() - 37))
        surface.blit(self.sheet.subsurface((0,188),(256,37)),(256,surface.get_height() - 37))

    def updates(self, dt, keys_pressed):
        self.keys = keys_pressed
        self.dt = dt

        if self.keys[f'{K_a}']:
            self.pass_stage_menu = True
            self.setFinish(False)
