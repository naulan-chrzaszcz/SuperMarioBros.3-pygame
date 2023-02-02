import pygame as pg

from fr.naulan.maps_creator.src.creator import Creator


class MapsCreator(object):
    FREQUENCY = 22050
    WIDTH = 1280
    HEIGHT = 720

    creator: Creator

    def __init__(self):
        pg.mixer.init(MapsCreator.FREQUENCY, -16, 2, 512)
        pg.init()
        pg.mouse.set_visible(True)

        screen = pg.display.set_mode((MapsCreator.WIDTH, MapsCreator.HEIGHT), 0, 32)
        display = pg.Surface((MapsCreator.WIDTH, MapsCreator.HEIGHT))

        self.creator = Creator(screen, display)
        self.creator.run()


MapsCreator()
