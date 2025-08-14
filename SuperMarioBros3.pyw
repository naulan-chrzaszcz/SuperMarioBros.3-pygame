"""
    "Fan Game" created by CHRZASZCZ Naulan.
        * Created the 26/09/2020 at 8:35am.
"""
import pygame as pg
import json
import yaml
import os

from pygame.locals import *

from src.fps import Fps
from src.window import Window
from src.select_menu_stage import StageMenu
from src.title_screen import TitleScreen
from src.scenes.scene_0 import Scene0
from src.maps_engine import Maps
from src.events import Events
from src.font import Font


class Main(object):
    window_size: Window.Size
    dt: float   # Time between two frame

    def __init__(self):
        with open("config.yaml") as config_file:
            self.config = yaml.safe_load(config_file)

        pg.mixer.init(
            self.config["mixer"]["frequency"],
            self.config["mixer"]["size"],
            self.config["mixer"]["channels"],
            self.config["mixer"]["buffer"]
        )
        pg.init()
        pg.joystick.init()
        pg.font.init()

        self.window_size = Window.Size(
            self.config["screen"]["width"],
            self.config["screen"]["height"]
        )
        self.screen = pg.display.set_mode(
            tuple(self.window_size),
            self.config["screen"]["flags"],
            self.config["screen"]["depth"]
        )
        self.display = pg.Surface((
            self.config["display"]["width"],
            self.config["display"]["height"]
        ))
        pg.mouse.set_visible(self.config["mouse"]["visible"])

        # Stock all Maps (Stages) in memory
        self.stage_list = {}
        self.t = 0

        # load all resources.
        print("-" * 3 + "= Loading resources =" + "-" * 11)
        with open(os.path.join("res", "pathIndex.json")) as f:
            pathIndex = json.load(f)
        self.res = {}
        for i in pathIndex:
            self.res[i] = {}
            for index in pathIndex[i]:
                if index != ":type":
                    directory = pathIndex[i][index][0]
                    file = pathIndex[i][index][1]
                    if pathIndex[i][":type"] == "image":
                        self.res[i][index] = self.load_img(os.path.join(directory, file))
                    elif pathIndex[i][":type"] == "music":
                        self.res[i][index] = pg.mixer.Sound(os.path.join(directory, file))
                    elif pathIndex[i][":type"] == "map":
                        with open(os.path.join(directory, file)) as f:
                            self.res[i][index] = json.load(f)
                    print(f"{pathIndex[i][index][1]} loaded !")
        print("-" * 3 + "= all resources loaded =" + "-" * 11 + "\n")

        with open("save.yaml") as save_file:
            self.save = yaml.safe_load(save_file)

        self.stage_menu = StageMenu()
        # Keyboard event and/or remote control
        self.event = Events(self.res["annexe"])
        # Intro CHRZASZCZ Development.
        self.scene_0 = Scene0(self.res)
        # Title screen of Super Mario Bros3.
        self.title_screen = TitleScreen(self.res)

        self.font_custom = Font()
        self.maps = Maps()
        self.fps = Fps()

    @staticmethod
    def load_img(directory, color_key=(255, 174, 201)):
        img = pg.image.load(directory).convert()
        img.set_colorkey(color_key)
        return img

    def run(self):
        while True:
            # FPS MANAGEMENT
            self.dt = self.fps.manage(fps=0)
            if self.fps.benchmark and int(self.t)%15 == 0:
                self.fps.get(); self.fps.average()
            self.t += (1 * self.dt)

            # Scene n°0
            if not self.scene_0.getFinish():
                self.scene_0.start(self.display, self.dt)
            else:
                if len(self.event.joysticks) != 0 and not self.event.is_calibrate:
                    self.event.calibrate(self.display)
                    self.screen.blit(pg.transform.scale(self.display, (self.window_size[0], self.window_size[1])), (0, 0))
                else:
                    self.event.get()
                    # LOAD
                    # select stage maps
                    if not self.title_screen.getIsTitle() and not self.stage_menu.load_stage_menu:
                        self.display.fill((0, 0, 0))
                        print("Game: Load stage menu...")
                        self.stage_menu.new(self.res)
                        print("Game: Stage menu is loaded !")
                        self.stage_menu.load_stage_menu = True
                    # maps
                    elif not self.stage_menu.load_maps and self.stage_menu.pass_maps:
                        self.display.fill((0, 0, 0))
                        print("Game: Load maps...")
                        self.maps.new(self.res, self.stage_menu.stage)
                        print("Game: Maps is loaded !")
                        self.stage_menu.load_maps = True

                    # DRAWs
                    if self.title_screen.getIsTitle():
                        self.title_screen.draw(self.display)
                    if self.title_screen.getPassStageMenu():
                        self.stage_menu.draw(self.display)
                    if self.stage_menu.pass_maps:
                        self.maps.draw(self.display)
                    # HUD
                    if not self.title_screen.getIsTitle():
                        hud_sheet = self.res["tiles"]["HUDSheet"]
                        pg.draw.rect(self.display, (0, 0, 0), Rect(0, self.display.get_height() - 45, self.display.get_width(), 45))
                        self.display.blit(hud_sheet.subsurface(0, 0, 154, 30), (self.display.get_width() / 6, self.display.get_height() - 40))
                        self.display.blit(hud_sheet.subsurface(155, 0, 74, 30), (self.display.get_width() / 1.5, self.display.get_height() - 40))
                        self.font_custom.draw_msg(self.display, [self.display.get_width() / 6 + 133, self.display.get_height() - 33], f'{self.stage_menu.player.coins}') if self.stage_menu.is_menu_stage else self.font_custom.draw_msg(self.display, [98, 192], f'{self.maps.player.coins}')
                        self.font_custom.draw_msg(self.display, [self.display.get_width() / 6 + 105, self.display.get_height() - 25], f'{self.stage_menu.player.score}', True) if self.stage_menu.is_menu_stage else self.font_custom.draw_msg(self.display, [98, 192], f'{self.maps.player.score}', True)
                        self.font_custom.draw_msg(self.display, [self.display.get_width() / 6 + 28, self.display.get_height() - 25], f'{self.stage_menu.player.life}') if self.stage_menu.is_menu_stage else self.font_custom.draw_msg(self.display, [98, 192], f'{self.maps.player.life}')
                        self.font_custom.draw_msg(self.display, [self.display.get_width() / 6 + 35, self.display.get_height() - 33], self.stage_menu.stage)

                    # UPDATES
                    if self.title_screen.getIsTitle():
                        self.title_screen.updates(self.dt, self.event.keys_pressed)
                    if all([self.title_screen.getPassStageMenu(), self.stage_menu.load_stage_menu, not self.stage_menu.pass_maps]):
                        self.stage_menu.updates(self.dt, self.event.keys_pressed)
                    if self.stage_menu.pass_maps and self.stage_menu.load_maps:
                        self.maps.updates(self.dt, self.event.keys_pressed)

            self.screen.blit(pg.transform.scale(self.display, tuple(self.window_size)), (0, 0))
            self.fps.draw(self.screen)  # Monitoring
            pg.display.update()


main = Main()
main.run()
