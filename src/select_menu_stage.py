import json
import os

from pygame.transform import rotate, flip
from pygame import draw, sprite, mixer
from pygame.locals import K_a

from src.scenes.scene_2 import Scene2
from src.scenes.scene_3 import Scene3
from src.entitys.player import Player
from src.entitys.cactus import Cactus
from src.maps_engine import Camera


class StageMenu(object):
    sfx: dict
    scene2: Scene2
    scene3: Scene3

    def __init__(self):

        self.all_sprites = sprite.LayeredUpdates()
        self.directory = 'res/matrices/'

        # ### BOOLEAN VARIABLES ###
        self.load_stage_menu = False
        self.is_menu_stage = True
        self.load_maps = False
        self.pass_maps = False
        self.select = False
        self.on_case = False

        # ### INT/FLOAT VARIABLES ###
        self.stage = '1'
        self.dt = 0

        # ### LIST VARIABLES ###
        self.all_tiles = []
        self.all_tiles_rect = []
        self.all_cactus = []

    def new(self, res):
        mixer.stop()

        res["musics"]["StageMenuMsc"].play(loops=-1)
        self.sfx = res["sfx"]
        self.sfx["enterWorld"].set_volume(.5); self.sfx["mapTravel"].set_volume(.5); self.sfx["newWorld"].set_volume(.5)

        data = res["levels"]["selectMenuStage"]
        tile_width = len(data['0'])
        tile_height = len(data)
        self.camera = Camera([tile_width * 16, tile_height * 16])

        # Load stages map
        with open(os.path.join("res/", "indexSheetImages.json")) as f:
            locSheet = json.load(f)
        for lgn in range(len(data)):
            n = 0
            for target, tile in enumerate(data[str(lgn)]):
                if tile is not None:
                    x, y = (target*16, lgn*16)
                    tilesIndex = ["C1","C2","C3","C4","C5","C6","GO","R0","R1","R2","R3","R4","R5","R6","V0","V1","V2",
                                  "V3","V4","V5","V6","00","PT","AY","CT"]
                    if tile[0] in tilesIndex:
                        if tile[0] != "CT":
                            r,w,h,l = locSheet[tile[0]]
                            if tile[0] == "R4":
                                self.all_tiles.append(rotate(res["tiles"]["selectMenuStageSheet"].subsurface(r,w,h,l),90))
                            elif tile[0] in ["R5","R6"]:
                                self.all_tiles.append(flip(res["tiles"]["selectMenuStageSheet"].subsurface(r,w,h,l),False,True))
                            else:
                                self.all_tiles.append(res["tiles"]["selectMenuStageSheet"].subsurface(r, w, h, l))
                            self.all_tiles_rect.append([self.all_tiles[n].get_rect(x=x,y=y),tile[0]])
                        else:
                            self.all_cactus.append(Cactus(self,res["tiles"]["selectMenuStageSheet"],[x,y]))
                    if tile[0] == "GO":
                        self.player = Player(self,[res["entities"]["player"]],[x,y])
                    n += 1 if tile[0] != "CT" else 0

        self.scene_2 = Scene2(res)
        self.scene_3 = Scene3()

    def draw(self, surface):
        surface.fill((0, 0, 0))
        draw.line(surface, (248, 236, 160), (0, 8), (surface.get_width(), 8), 3)
        draw.line(surface, (248, 236, 160), (surface.get_width(), 184), (0, 184), 3)

        # Draw all cactus on the screen
        for target in self.all_cactus:
            surface.blit(target.image, self.camera.apply(target))
        # Draw other tiles on the screen
        for target, img in enumerate(self.all_tiles):
            surface.blit(img, self.camera.apply_rect(self.all_tiles_rect[target][0]))

        # Play first animation if it not finish ("welcome" animation)
        if not self.scene_2.finish:
            self.scene_2.start(surface, self.dt, [self.player.life, self.stage, self.player.who], self.sfx)
        # Draw the player after "welcome" animation
        elif self.scene_2.finish:
            surface.blit(self.player.image, self.camera.apply(self.player))
            if self.on_case and self.select: self.scene_3.start(surface, self.dt, self.sfx)

    def updates(self, dt, keys_pressed):
        self.dt = dt

        # Animate all cactus and test collide with a player
        for n in range(len(self.all_cactus)):
            self.player.collide_test(self.all_cactus[n]) if all([self.scene_2.finish, self.select == 0]) else None
            self.all_cactus[n].update(dt)

        # Updates the player after a scene n°2
        if all([self.scene_2.finish, self.select == 0]):
            self.player.keys = keys_pressed
            self.player.update(dt)

            if keys_pressed[f'{K_a}']:
                self.select = True

        # Collide test
        collision_tolerance = 10
        for target in range(len(self.all_tiles_rect)):
            if self.player.rect.colliderect(self.all_tiles_rect[target][0]):
                # Collide with stage n°1 case
                if self.all_tiles_rect[target][1] == 'C1':
                    self.stage = '1'
                    self.on_case = 1
                    if abs(self.player.rect.centerx - self.all_tiles_rect[target][0].centerx) < collision_tolerance:
                        if self.select and self.scene_3.finish:
                            self.load_maps = 0
                            self.pass_maps = 1
                            self.select = False
                            return self.load_maps, self.pass_maps, self.on_case
                elif self.all_tiles_rect[target][1] == 'C2':
                    self.stage = '2'
                    self.on_case = 1
                    if abs(self.player.rect.centerx - self.all_tiles_rect[target][0].centerx) < collision_tolerance:
                        if self.select and self.scene_3.finish:
                            self.load_maps = 0
                            self.pass_maps = 1
                            self.select = False
                            return self.load_maps, self.pass_maps, self.on_case

                # Collide with other tiles
                if any([self.all_tiles_rect[target][1] == '00', self.all_tiles_rect[target][1] == 'AY',
                        self.all_tiles_rect[target][1] == 'V0', self.all_tiles_rect[target][1] == 'V1',
                        self.all_tiles_rect[target][1] == 'V2', self.all_tiles_rect[target][1] == 'V3',
                        self.all_tiles_rect[target][1] == 'V4', self.all_tiles_rect[target][1] == 'V5']):
                    if abs(self.player.rect.right - self.all_tiles_rect[target][
                        0].left) < collision_tolerance:   self.player.rect.right = self.all_tiles_rect[target][0].left
                    if abs(self.player.rect.left - self.all_tiles_rect[target][
                        0].right) < collision_tolerance:   self.player.rect.left = self.all_tiles_rect[target][0].right
                    if abs(self.player.rect.top - self.all_tiles_rect[target][
                        0].bottom) < collision_tolerance:   self.player.rect.top = self.all_tiles_rect[target][0].bottom
                    if abs(self.player.rect.bottom - self.all_tiles_rect[target][
                        0].top) < collision_tolerance:   self.player.rect.bottom = self.all_tiles_rect[target][0].top
