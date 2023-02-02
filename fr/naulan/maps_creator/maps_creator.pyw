import pygame as pg

from fr.naulan.maps_creator.src.creator import Creator
from fr.naulan.maps_creator.src.ui.button_builder import ButtonBuilder


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

        button_builder = ButtonBuilder()
        button_builder.set_x(50)
        button_builder.set_y(50)
        button_builder.set_text("Click !", (255, 255, 255))
        button_builder.set_color_background((255, 185, 45))
        button_builder.set_surface(screen)
        button_builder.set_height(50)
        button_builder.set_width(100)

        while True:
            screen.fill((0, 0, 0))

            for event in pg.event.get():
                pass

            button_builder.button.blit()
            pg.display.update()

        self.creator = Creator(screen, display)
        self.creator.run()


MapsCreator()
