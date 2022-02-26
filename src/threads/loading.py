import pygame as pg
import json
import os

from pygame.threads import Thread


class Loading(Thread):
    
    def __init__(self, obj):
        super().__init__()
        self.name = "Thread ressources loader"

        self.loading_bar = 0.00
        self.obj = obj

    @staticmethod
    def load_img(directory,color_key=(255,174,201)):
        img = pg.image.load(directory).convert()
        img.set_colorkey(color_key)
        return img

    def run(self):
        super(Loading, self).run()

        print("Starting of " + self.getName() + " ...")

        # load save
        print("-"*3 + "= loading save file =" + "-"*11)
        with open(os.path.join("res","save.json")) as f:
            self.obj.save = json.load(f)

        # load all resources.
        print("-"*3 + "= Loading resources =" + "-"*11)
        with open(os.path.join("res","pathIndex.json")) as f:
            pathIndex = json.load(f)
        for i in pathIndex:
            self.obj.res[i] = {}
            for index in pathIndex[i]:
                if index != ":type":
                    directory = pathIndex[i][index][0]
                    file = pathIndex[i][index][1]
                    if pathIndex[i][":type"] == "image":
                        self.obj.res[i][index] = self.load_img(os.path.join(directory,file))
                    elif pathIndex[i][":type"] == "music":
                        self.obj.res[i][index] = pg.mixer.Sound(os.path.join(directory,file))
                    elif pathIndex[i][":type"] == "map":
                        with open(os.path.join(directory,file)) as f:
                            self.obj.res[i][index] = json.load(f)
                    print(f"{pathIndex[i][index][1]} loaded !")
            self.loading_bar += 1
        print("-"*3 + "= all resources loaded =" + "-"*11 + "\n")
