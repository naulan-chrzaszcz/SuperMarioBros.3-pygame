from math import sin
from typing import List

from pygame import Surface
from pygame.locals import *

from src.font import Font
from src.scenes.scene_1 import Scene1


class TitleScreen(Scene1):
    sheet: Surface
    t: List

    def __init__(self, sheet):
        super().__init__()
        self.sheet = sheet

        self.font = Font()
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
            # Title
            surface.blit(self.sheet.subsurface((0, 226), (179, 72)), (self.x, surface.get_height() / 5))
            # Blit "3" number
            surface.blit(self.sheet.subsurface((180, 226), (42, 41)), (self.x + 72, surface.get_height() / 4 + 62))
            # Draw decors
            surface.blit(self.sheet.subsurface((180, 268), (32, 16)), (self.x - 22, (surface.get_height() / 4 - 12) + sin(self.t[3]) * 5))
            surface.blit(self.sheet.subsurface((180, 285), (16, 8)), (self.x + 185, (surface.get_height() / 4 + 22) + sin(self.t[3] - 1) * 3.5))
            surface.blit(self.sheet.subsurface((257, 188), (64, 64)), (0, surface.get_height() - 101))
            surface.blit(self.sheet.subsurface((322, 188), (63, 93)), (surface.get_width() - 63, surface.get_height() - 133))
            # Text
            self.font.draw_msg(surface, [(surface.get_width() / 2.6) + sin(self.t[3]), surface.get_height() / 4 + 105], 'P')
            self.font.draw_msg(surface, [((surface.get_width() / 2.6) + sin(self.t[3] - 1) * 2) + 7, surface.get_height() / 4 + 105], 'R')
            self.font.draw_msg(surface, [((surface.get_width() / 2.6) + sin(self.t[3] - 2) * 2) + (7 * 2), surface.get_height() / 4 + 105], 'E')
            self.font.draw_msg(surface, [((surface.get_width() / 2.6) + sin(self.t[3] - 3) * 2) + (7 * 3), surface.get_height() / 4 + 105], 'S')
            self.font.draw_msg(surface, [((surface.get_width() / 2.6) + sin(self.t[3] - 4) * 2) + (7 * 4), surface.get_height() / 4 + 105], 'S')
            self.font.draw_msg(surface, [((surface.get_width() / 2.6) + sin(self.t[3] - 5) * 2) + (7 * 5) + 5, surface.get_height() / 4 + 105], 'A')
            self.font.draw_msg(surface, [((surface.get_width() / 2.6) + sin(self.t[3] - 6) * 2) + (7 * 6) + 10, surface.get_height() / 4 + 105], 'T')
            self.font.draw_msg(surface, [((surface.get_width() / 2.6) + sin(self.t[3] - 7) * 2) + (7 * 7) + 10, surface.get_height() / 4 + 105], 'O')
            self.font.draw_msg(surface, [((surface.get_width() / 2.6) + sin(self.t[3] - 8) * 2) + (7 * 8) + 15, surface.get_height() / 4 + 105], 'S')
            self.font.draw_msg(surface, [((surface.get_width() / 2.6) + sin(self.t[3] - 9) * 2) + (7 * 9) + 15, surface.get_height() / 4 + 105], 'T')
            self.font.draw_msg(surface, [((surface.get_width() / 2.6) + sin(self.t[3] - 10) * 2) + (7 * 10) + 15, surface.get_height() / 4 + 105], 'A')
            self.font.draw_msg(surface, [((surface.get_width() / 2.6) + sin(self.t[3] - 11) * 2) + (7 * 11) + 15, surface.get_height() / 4 + 105], 'R')
            self.font.draw_msg(surface, [((surface.get_width() / 2.6) + sin(self.t[3] - 12) * 2) + (7 * 12) + 15, surface.get_height() / 4 + 105], 'T')

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
