"""
    "Fan Game" created by CHRZASZCZ Naulan.
        * Created the 26/09/2020 at 8:35am.
"""
import pygame as pg

from loader import Loader
from src.game import Game


class Launcher(object):

    @staticmethod
    def frequency() -> int: return 22050
    @staticmethod
    def width_screen() -> int: return 1280
    @staticmethod
    def height_screen() -> int: return 720
    @staticmethod
    def game_width_resolution() -> int: return 464
    @staticmethod
    def game_height_resolution() -> int: return 240

    @staticmethod
    def launch():
        pg.mixer.init(Launcher.frequency(), -16, 2, 512)
        pg.init()
        pg.joystick.init()
        pg.font.init()
        pg.mouse.set_visible(False)

        game: Game = Game()
        Loader.load(game)
        game.load()

        window_size = (Launcher.width_screen(), Launcher.height_screen())
        screen = pg.display.set_mode(window_size, 0, 32)
        resolution: tuple = (Launcher.game_width_resolution(), Launcher.game_height_resolution())
        display = pg.Surface(resolution)

        game.run(screen, display)


Launcher.launch()
