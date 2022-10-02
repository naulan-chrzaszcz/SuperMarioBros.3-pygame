import json
import os
import pygame as pg

from pygame.sprite import LayeredUpdates

from src.blocks.floor import Floor
from src.blocks.lootBlock import LootBlock
from src.blocks.platform import Platform
from src.constantes import TILE_WIDTH
from src.entitys.cloud import Cloud
from src.entitys.coin import Coin
from src.entitys.goomba import Goomba
from src.entitys.koopa import Koopa
from src.entitys.vegetable import Vegetable
from src.events import Events
from src.font import Font
from src.fps import Fps
from src.maps_engine import Maps
from src.select_menu_stage import StageMenu
from src.title_screen import TitleScreen


class Game(object):

    dt: float   # Time between two frame
    sprites: LayeredUpdates

    res: dict = {}


    def __init__(self):
        self.sprites = pg.sprite.LayeredUpdates()

        # Stock all Maps (Stages) in memory
        self.stage_list = {}
        self.t = 0

        self.font_custom = Font()
        self.maps = Maps()
        self.fps = Fps()

    def load(self):
        # Updates save file
        with open(os.path.join("res","save.json"),"w") as f:
            json.dump(self.res["save"],f,indent=4)
        # Keyboard event and/or remote control
        self.event = Events(self.res["annexe"])
        # Title screen of Super Mario Bros3.
        self.title_screen = TitleScreen(self.res)
        self.stage_menu = StageMenu()

    @staticmethod
    def load_img(directory, color_key=(255, 174, 201)):
        img = pg.image.load(directory).convert()
        img.set_colorkey(color_key)
        return img

    def run(self, screen, display):
        while True:
            # FPS MANAGEMENT
            self.dt = self.fps.manage(fps=144)
            if self.fps.benchmark and int(self.t)%15 == 0:
                self.fps.get(); self.fps.average()
            self.t += (1 * self.dt)

            if len(self.event.joysticks) != 0 and not self.event.is_calibrate:
                self.event.calibrate(display)
                screen.blit(pg.transform.scale(display, (1280, 720)), (0, 0))
            else:
                self.event.get()
                # LOAD
                # select stage maps
                if not self.title_screen.getIsTitle() and not self.stage_menu.load_stage_menu:
                    display.fill((0, 0, 0))
                    print("Game: Load stage menu...")
                    self.stage_menu.new(self.res)
                    print("Game: Stage menu is loaded !")
                    self.stage_menu.load_stage_menu = True
                # maps
                elif not self.stage_menu.load_maps and self.stage_menu.pass_maps:
                    display.fill((0, 0, 0))
                    print("Game: Load maps...")
                    self.player = self.maps.new(self.sprites, self.res, self.stage_menu.stage)
                    print("Game: Maps is loaded !")
                    self.stage_menu.load_maps = True

                # DRAWs
                if self.title_screen.getIsTitle():
                    self.title_screen.draw(display)
                if self.title_screen.getPassStageMenu():
                    self.stage_menu.draw(display)
                if self.stage_menu.pass_maps:
                    display.fill((156, 252, 240))

                    for sprite in self.sprites:
                        if isinstance(sprite, Platform):
                            if all([self.maps.camera.rect.left + 16 >= -sprite.rect.left, (TILE_WIDTH - self.maps.camera.rect.left + 390) >= sprite.rect.left]):
                                display.blit(sprite.image, self.maps.camera.apply(sprite))
                                if any([sprite.offset_img[0] == 5, sprite.offset_img[0] == 2,sprite.offset_img[0] == 3]):
                                    sprite.apply_shadow(display, self.maps.camera)

                        if isinstance(sprite, Floor):
                            if all([self.maps.camera.rect.left + 16 >= -sprite.rect.left, (TILE_WIDTH - self.maps.camera.rect.left + 390) >= sprite.rect.left]):
                                display.blit(sprite.image, self.maps.camera.apply(sprite))

                        if isinstance(sprite, LootBlock):
                            if len(sprite.mushrooms) != 0:
                                for mush in sprite.mushrooms:
                                    if all([self.maps.camera.rect.left + 16 >= -mush.rect.left, (TILE_WIDTH - self.maps.camera.rect.left + 390) >= mush.rect.left]):
                                        display.blit(mush.image, self.maps.camera.apply(mush))
                            if all([self.maps.camera.rect.left + 16 >= -sprite.rect.left, (TILE_WIDTH - self.maps.camera.rect.left + 390) >= sprite.rect.left]):
                                display.blit(sprite.image, self.maps.camera.apply(sprite))

                        if isinstance(sprite, Vegetable) or isinstance(sprite, Coin) or isinstance(sprite, Cloud):
                            if all([self.maps.camera.rect.left + 16 >= -sprite.rect.left, (TILE_WIDTH - self.maps.camera.rect.left + 390) >= sprite.rect.left]):
                                display.blit(sprite.image, self.maps.camera.apply(sprite))

                        if isinstance(sprite, Goomba) or isinstance(sprite, Koopa) or isinstance(sprite, Coin):
                            if sprite.step == 1:
                                self.sprites.remove(sprite)
                            if all([self.maps.camera.rect.left + 16 >= -sprite.rect.left, (TILE_WIDTH - self.maps.camera.rect.left + 390) >= sprite.rect.left]):
                                display.blit(sprite.image, self.maps.camera.apply(sprite))

                    display.blit(self.player.image, self.maps.camera.apply(self.player))
                # HUD
                if not self.title_screen.getIsTitle():
                    hud_sheet = self.res["tiles"]["HUDSheet"]
                    pg.draw.rect(display,(0, 0, 0), pg.Rect(0,display.get_height() - 45,display.get_width(),45))
                    display.blit(hud_sheet.subsurface(0, 0, 154, 30), (display.get_width() / 6, display.get_height() - 40))
                    display.blit(hud_sheet.subsurface(155, 0, 74, 30), (display.get_width() / 1.5, display.get_height() - 40))
                    self.font_custom.draw_msg(display, [display.get_width() / 6 + 133, display.get_height() - 33], f'{self.stage_menu.player.coins}') if self.stage_menu.is_menu_stage else self.font_custom.draw_msg(display, [98, 192], f'{self.maps.player.coins}')
                    self.font_custom.draw_msg(display, [display.get_width() / 6 + 105, display.get_height() - 25], f'{self.stage_menu.player.score}', True) if self.stage_menu.is_menu_stage else self.font_custom.draw_msg(display, [98, 192], f'{self.maps.player.score}', True)
                    self.font_custom.draw_msg(display, [display.get_width() / 6 + 28, display.get_height() - 25], f'{self.stage_menu.player.life}') if self.stage_menu.is_menu_stage else self.font_custom.draw_msg(display, [98, 192], f'{self.maps.player.life}')
                    self.font_custom.draw_msg(display, [display.get_width() / 6 + 35, display.get_height() - 33], self.stage_menu.stage)

                # UPDATES
                if self.title_screen.getIsTitle():
                    self.title_screen.updates(self.dt, self.event.keys_pressed)
                if all([self.title_screen.getPassStageMenu(), self.stage_menu.load_stage_menu, not self.stage_menu.pass_maps]):
                    self.stage_menu.updates(self.dt, self.event.keys_pressed)
                if self.stage_menu.pass_maps and self.stage_menu.load_maps:
                    self.maps.updates(self.dt, self.event.keys_pressed, self.sprites)

            screen.blit(pg.transform.scale(display, (1280, 720)), (0, 0))
            self.fps.draw(screen)  # Monitoring
            pg.display.update()

