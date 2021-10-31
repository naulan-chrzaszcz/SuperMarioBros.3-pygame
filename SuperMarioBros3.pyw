"""
    "Fan Game" created by CHRZASZCZ Naulan.
        * Created the 26/09/2020 at 8:35am.
"""
import subprocess
import pygame as pg
import ctypes
import json
import sys
import os

from typing import List
from src.fps import Fps
from pygame.locals import *
from os import getpid

from src.error_management import ErrorManagement
from src.select_menu_stage import StageMenu
from src.title_screen import TitleScreen
from src.scenes.scene_0 import Scene0
from src.maps_engine import Maps
from src.events import Events
from src.font import Font


pg.mixer.init(22050, -16, 2, 512)
pg.init()
pg.joystick.init()
pg.font.init()


class Main(object):
    window_size: List[int]

    def __init__(self):
        # OS Check
        operating_system = sys.platform
        print(f"(!) Info: Le jeux est lancée sur \"{operating_system}\".")
        if operating_system.lower() == "win32":  # for Windows OS
            self.__shouldClose = [0]
            self.windows_startup_settings()
        elif operating_system.lower() in ["linux", "linux2"]:  # for Linux OS
            self.linux_startup_settings()
        else:
            print("(!) Warning: La resolution native n'a pas étais trouvé !")
            self.window_size = [1280, 720]
        w, h = self.window_size
        print(f"(!) Info: Resolution native -> {w}x{h}")
        # Create Window and Display Surface
        self.screen = pg.display.set_mode((w, h), 0, 32)
        self.display = pg.Surface((464, 240))
        # Hide mouse
        pg.mouse.set_visible(False)

        # Stock all Maps (Stages) in memory
        self.stage_list = {}

        self.t = 0

        # load all resources.
        print("---= Loading resources =-----------")
        with open(os.path.join("res", "pathIndex.json")) as f:
            pathIndex = json.load(f)
        self.res = {}
        for i in pathIndex:
            self.res[i] = {}
            for index in pathIndex[i]:
                if index != ":type":
                    directory = pathIndex[i][index][0]; file = pathIndex[i][index][1]
                    if pathIndex[i][":type"] == "image":
                        self.res[i][index] = self.load_img(os.path.join(directory, file))
                    elif pathIndex[i][":type"] == "music":
                        self.res[i][index] = pg.mixer.Sound(os.path.join(directory, file))
                    elif pathIndex[i][":type"] == "map":
                        with open(os.path.join(directory, file)) as f:
                            self.res[i][index] = json.load(f)
                    print(f"{pathIndex[i][index][1]} loaded !")
        print("---= all resources loaded =-----------")

        self.stage_menu = StageMenu()
        # Keyboard event and/or remote control
        self.event = Events(self.res["annexe"])
        # Intro CHRZASZCZ Development.
        self.scene_0 = Scene0(self.res["annexe"], self.res["sfx"]["bass"], self.event.keys_pressed)
        # Title screen of Super Mario Bros3.
        self.title_screen = TitleScreen(self.res["tiles"]["titleScreenSheet"])

        self.font_custom = Font()
        self.maps = Maps()
        self.fps = Fps()

    def windows_startup_settings(self):
        """ Apply and get some settings for Windows.
                Priority set to High
                Get native resolution.
            (Use ctypes libraries) """
        # For priority program.
        self.get_priority_class = ctypes.windll.kernel32.GetPriorityClass
        self.set_priority_class = ctypes.windll.kernel32.SetPriorityClass
        self.open_process = ctypes.windll.kernel32.OpenProcess
        self.close_handle = ctypes.windll.kernel32.CloseHandle
        # Get native resolution.
        user32 = ctypes.windll.user32
        self.window_size = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]
        # Set the game in priority "high" in Windows (for performance in game).
        self.set_priority(0x0080)

    def linux_startup_settings(self):
        """ Get and apply some settings for Linux.
                Priority set to High
                Get native resolution.
            (Use shell with subprocess libraries) """
        # Process priority.
        os.nice(1)
        # Get native resolution.
        output = str(subprocess.Popen('xrandr | grep "\*" | cut -d" " -f4',
                                      shell=True,
                                      stdout=subprocess.PIPE).communicate()[0])
        w, h = output.split('x')
        # Remove useless element for correctly int conversion.
        self.window_size = [int(f"{w}".replace("b'", "")), int(f"{h}".replace("\\n'", ""))]

    @staticmethod
    def load_img(directory, color_key=(255, 174, 201)):
        img = pg.image.load(directory).convert()
        img.set_colorkey(color_key)
        return img

    def get_process_handle(self, process, inherit=False):
        self.__shouldClose[0] = 1
        process = getpid() if not process else 0
        return self.open_process(ctypes.c_uint(0x0200 | 0x0400), ctypes.c_bool(inherit), ctypes.c_uint(process))

    def set_priority(self, priority, process=None, inherit=None):
        if not process: process = self.get_process_handle(None, inherit)
        result = self.set_priority_class(process, ctypes.c_uint(priority)) != 0
        if self.__shouldClose:
            self.close_handle(process)
            self.__shouldClose[0] = 0
        return result

    def run(self):
        while True:
            # ### --= FPS MANAGEMENT =-- ###
            self.dt = self.fps.manage(fps=120)
            if all([self.fps.benchmark, int(self.t)%15 == 0]):
                self.fps.get()
                self.fps.average()
            self.t += (1 * self.dt)
            # ### ---------------------- ###

            if self.scene_0.finish != 1:
                self.scene_0.start(self.display, self.dt)
                self.screen.blit(pg.transform.scale(self.display, (self.window_size[0], self.window_size[1])), (0, 0))
            else:
                if len(self.event.joysticks) != 0 and self.event.is_calibrate is False:
                    self.event.calibrate(self.display)
                    self.screen.blit(pg.transform.scale(self.display, (self.window_size[0], self.window_size[1])), (0, 0))
                else:
                    self.event.get()

                    # ### -------=LOAD=------- ###
                    # Load select stage maps
                    if all([self.title_screen.is_title == 0, self.stage_menu.load_stage_menu == 0]):
                        self.display.fill((0, 0, 0))
                        print("Game: Load stage menu...")
                        self.stage_menu.new(self.res)
                        print("Game: Stage menu is loaded !")
                        self.stage_menu.load_stage_menu = True

                    # Load maps
                    elif all([self.stage_menu.load_maps == 0, self.stage_menu.pass_maps]):
                        self.display.fill((0, 0, 0))
                        print("Game: Load maps...")
                        self.maps.new(self.res, self.stage_menu.stage)
                        print("Game: Maps is loaded !")
                        self.stage_menu.load_maps = True
                    # ### -------------------- ###

                    # ### -------=DRAW=------- ###
                    self.title_screen.draw(self.display) if self.title_screen.is_title else None
                    self.stage_menu.draw(self.display) if self.title_screen.pass_stage_menu else None
                    self.maps.draw(self.display) if self.stage_menu.pass_maps else None
                    # HUD
                    if self.title_screen.is_title is not True:
                        hud_sheet = self.res["tiles"]["HUDSheet"]
                        pg.draw.rect(self.display, (0, 0, 0),
                                     Rect(0, self.display.get_height() - 45, self.display.get_width(), 45))
                        self.display.blit(hud_sheet.subsurface(0, 0, 154, 30),
                                          (self.display.get_width() / 6, self.display.get_height() - 40))
                        self.display.blit(hud_sheet.subsurface(155, 0, 74, 30),
                                          (self.display.get_width() / 1.5, self.display.get_height() - 40))
                        self.font_custom.draw_msg(self.display,
                                                  [self.display.get_width() / 6 + 133, self.display.get_height() - 33],
                                                  f'{self.stage_menu.player.coins}') if self.stage_menu.is_menu_stage else self.font_custom.draw_msg(
                            self.display, [98, 192], f'{self.maps.player.coins}')
                        self.font_custom.draw_msg(self.display,
                                                  [self.display.get_width() / 6 + 105, self.display.get_height() - 25],
                                                  f'{self.stage_menu.player.score}',
                                                  True) if self.stage_menu.is_menu_stage else self.font_custom.draw_msg(
                            self.display, [98, 192], f'{self.maps.player.score}', True)
                        self.font_custom.draw_msg(self.display,
                                                  [self.display.get_width() / 6 + 28, self.display.get_height() - 25],
                                                  f'{self.stage_menu.player.life}') if self.stage_menu.is_menu_stage else self.font_custom.draw_msg(
                            self.display, [98, 192], f'{self.maps.player.life}')
                        self.font_custom.draw_msg(self.display,
                                                  [self.display.get_width() / 6 + 35, self.display.get_height() - 33],
                                                  self.stage_menu.stage)
                    # Scale surface to native screen size
                    self.screen.blit(pg.transform.scale(self.display, (self.window_size[0], self.window_size[1])),
                                     (0, 0))
                    # Monitoring
                    self.fps.draw(self.screen)
                    # ### -------------------- ###

                    # ### ------=UPDATES=----- ###
                    self.title_screen.updates(self.dt, self.event.keys_pressed) if self.title_screen.is_title else None
                    self.stage_menu.updates(self.dt, self.event.keys_pressed) if all(
                        [self.title_screen.pass_stage_menu, self.stage_menu.load_stage_menu,
                         self.stage_menu.pass_maps == 0]) else None
                    self.maps.updates(self.dt,
                                      self.event.keys_pressed) if self.stage_menu.pass_maps and self.stage_menu.load_maps else None
                    # ### -------------------- ###
            pg.display.update()


main = Main()
main.run()
