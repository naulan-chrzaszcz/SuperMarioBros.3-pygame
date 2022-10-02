import pygame as pg
import json
import os

from threading import Thread

from src.fps import Fps
from src.game import Game
from src.scenes.scene_0 import Scene0


class LoadingThread(Thread):

    name: str = "Thread ressources loader"
    loading_bar: int = 0
    game: Game

    def __init__(self, game: Game):
        super().__init__()
        self.game = game

    @staticmethod
    def load_img(directory, color_key=(255, 174, 201)):
        img = pg.image.load(directory).convert()
        img.set_colorkey(color_key)
        return img

    def run(self):
        super(LoadingThread, self).run()
        print("Starting of " + self.getName() + " ...")

        data = {}

        # load save
        print(("-"*3) + "= loading save file =" + ("-"*11))
        with open(os.path.join("res", "save.json")) as f:
            data["save"] = json.load(f)

        # load all resources.
        print(("-"*3) + "= LoadingThread resources =" + ("-"*11))
        with open(os.path.join("res", "pathIndex.json")) as f:
            pathIndex = json.load(f)
        for part in pathIndex:
            data[part] = {}
            for target in pathIndex[part]:
                if target != ":type":
                    directory = pathIndex[part][target][0]
                    file = pathIndex[part][target][1]

                    if pathIndex[part][":type"] == "image":
                        data[part][target] = self.load_img(
                            os.path.join(directory, file))
                    elif pathIndex[part][":type"] == "music":
                        data[part][target] = pg.mixer.Sound(
                            os.path.join(directory, file))
                    elif pathIndex[part][":type"] == "map":
                        with open(os.path.join(directory, file)) as f:
                            data[part][target] = json.load(f)
                    print(f"{pathIndex[part][target][1]} loaded !")
            self.loading_bar += 1
        print("-"*3 + "= all resources loaded =" + "-"*11 + "\n")

        self.game.res = data


class IntroductionThread(Thread):

    name: str = "Thread loading progress bar with an introduction scene"
    width_window_intro: int = 640
    height_window_intro: int = 480
    game_width_resolution: int = 464
    game_height_resolution: int = 240
    color_bar_progress: tuple = (255, 255, 255)
    scene_0: Scene0 = Scene0()

    def __init__(self, loader_ressource_thread):
        super().__init__()

        self.loader_ressource_thread = loader_ressource_thread
        self.fps = Fps()

        self.screen = pg.display.set_mode((self.width_window_intro, self.height_window_intro), pg.NOFRAME)
        self.display = pg.Surface((self.game_width_resolution, self.game_height_resolution))

        self.dt = 0

    def run(self) -> None:
        super(IntroductionThread, self).run()
        print("Starting of " + self.getName() + " ...")

        while self.loader_ressource_thread.is_alive():
            self.display.fill((0, 0, 0))
            self.dt = self.fps.manage(fps=60)

            # Intro CHRZASZCZ Development.
            self.scene_0.start(self.display, self.dt)

            # progress bar
            pg.draw.line(self.display, self.color_bar_progress, (5, self.game_height_resolution - 10), ((5 + (self.loader_ressource_thread.loading_bar/7)*100)*4, self.game_height_resolution - 10))
            self.screen.blit(pg.transform.scale(self.display, (self.width_window_intro, self.height_window_intro)), (0, 0))
            pg.display.update()


class Loader(object):

    loader_ressource: LoadingThread
    introduction: IntroductionThread

    @staticmethod
    def load(game: Game):
        loader_ressource = LoadingThread(game)
        introduction = IntroductionThread(loader_ressource)

        loader_ressource.start()
        introduction.start()
        # Bloque le Thread principal du programme tant que sa charge les ressources du jeu
        while loader_ressource.is_alive() and introduction.is_alive():
            pass
