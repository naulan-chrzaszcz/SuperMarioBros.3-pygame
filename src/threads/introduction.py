import pygame as pg

from pygame.threads import Thread

from src.fps import Fps
from src.scenes.scene_0 import Scene0


class Introduction(Thread):

    def __init__(self, screen, surface, window_size, res_thread):
        super().__init__()
        self.scene_0 = Scene0({"annexe": {"introBG": pg.image.load("res/sheets/intro-bg.png")}})
        self.res_thread = res_thread
        self.fps = Fps()

        self.screen = screen
        self.surface: pg.Surface = surface

        self.window_size = window_size
        self.dt = 0

    def run(self) -> None:
        while self.res_thread.is_alive():
            self.surface.fill((0,0,0))
            self.dt = self.fps.manage(fps=0)

            # Intro CHRZASZCZ Development.
            self.scene_0.start(self.surface, self.dt)

            # progress bar
            pg.draw.line(self.surface, (255, 255, 255), (5, self.surface.get_height()-10), ((5 + (self.res_thread.loading_bar/7)*100)*4, self.surface.get_height()-10))
            self.screen.blit(pg.transform.scale(self.surface, self.window_size), (0, 0))
            pg.display.update()
