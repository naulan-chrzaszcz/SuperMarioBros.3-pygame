import pygame as pg
import json
import os

from threading import Thread

from src.fps import Fps
from src.game import Game
from src.scenes.scene_0 import Scene0


class Loader(object):

    @staticmethod
    def load(game: Game):
        loading_res = Loading(game)
        introduction = Introduction(loading_res)
        loading_res.start()
        introduction.start()

        # Bloque le Thread principal du programme tant que sa charge les ressources du jeu
        while loading_res.is_alive() and introduction.is_alive():
            pass


class Loading(Thread):

    name: str
    loading_bar: int
    game: Game


    def __init__(self, game: Game):
        super().__init__()
        self.game = game
        self.name = "Thread ressources loader"

        self.loading_bar = 0

    @staticmethod
    def load_img(directory,color_key=(255,174,201)):
        img = pg.image.load(directory).convert()
        img.set_colorkey(color_key)
        return img

    def run(self):
        super(Loading,self).run()
        print("Starting of " + self.getName() + " ...")

        data = {}

        # load save
        print(("-"*3) + "= loading save file =" + ("-"*11))
        with open(os.path.join("res","save.json")) as f:
            data["save"] = json.load(f)

        # load all resources.
        print(("-"*3) + "= Loading resources =" + ("-"*11))
        with open(os.path.join("res","pathIndex.json")) as f:
            pathIndex = json.load(f)
        for part in pathIndex:
            data[part] = {}
            for target in pathIndex[part]:
                if target != ":type":
                    directory = pathIndex[part][target][0]
                    file = pathIndex[part][target][1]

                    if pathIndex[part][":type"] == "image":
                        data[part][target] = self.load_img(os.path.join(directory,file))
                    elif pathIndex[part][":type"] == "music":
                        data[part][target] = pg.mixer.Sound(os.path.join(directory,file))
                    elif pathIndex[part][":type"] == "map":
                        with open(os.path.join(directory,file)) as f:
                            data[part][target] = json.load(f)
                    print(f"{pathIndex[part][target][1]} loaded !")
            self.loading_bar += 1
        print("-"*3 + "= all resources loaded =" + "-"*11 + "\n")

        self.game.res = data


class Introduction(Thread):

    name: str = "Thread loading progress bar with an introduction scene"


    def __init__(self, res_thread):
        super().__init__()

        self.scene_0 = Scene0()
        self.res_thread = res_thread
        self.fps = Fps()

        self.screen = pg.display.set_mode((640, 480), pg.NOFRAME)
        self.display = pg.Surface((464, 240))

        self.dt = 0

    def run(self) -> None:
        super(Introduction, self).run()
        print("Starting of " + self.getName() + " ...")

        while self.res_thread.is_alive():
            self.display.fill((0, 0, 0))
            self.dt = self.fps.manage(fps=0)

            # Intro CHRZASZCZ Development.
            self.scene_0.start(self.display, self.dt)

            # progress bar
            pg.draw.line(self.display,(255,255,255),(5,self.display.get_height() - 10),((5 + (self.res_thread.loading_bar/7)*100)*4,self.display.get_height() - 10))
            self.screen.blit(pg.transform.scale(self.display, (640, 480)), (0, 0))
            pg.display.update()
