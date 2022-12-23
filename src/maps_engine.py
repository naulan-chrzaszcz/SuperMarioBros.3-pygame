import json
import os

from pygame import Rect,sprite,mixer

from src.entities.vegetable import Vegetable
from src.blocks.lootBlock import LootBlock
from src.blocks.platform import Platform
from src.entities.goomba import Goomba
from src.entities.player import Player
from src.entities.koopa import Koopa
from src.entities.cloud import Cloud
from src.blocks.floor import Floor
from src.entities.coin import Coin


class Camera(object):

    def __init__(self,size):
        # ### INT/FLOAT VARIABLES ###
        self.width = size[0]
        self.height = size[1]

        # ### RECT VARIABLES ###
        self.rect = Rect(0,0,size[0],size[1])

        self.apply_rect = lambda rect: rect.move(self.rect.topleft)

    def apply(self, entity, add_x=0, add_y=0):
        return entity.rect.move((self.rect.topleft[0] + add_x), (self.rect.topleft[1] + add_y))

    def update(self,target):
        x = -target.rect.x + 100
        y = -target.rect.y

        # limit scrolling to map size
        x = min(0,x)  # left
        y = min(0,y)  # top
        x = max(-self.width,x)  # right
        y = max(-(self.height - 237),y)  # bottom
        self.rect.update(x,y,self.width,self.height)


class Maps(object):
    allTiles = [tile for tile in "fa0,fa1,fa2,fa3,fa4,fa5,pg0,pg1,pg2,pg3,pg4,pg5,pg6,pg7,pg8,pp0,pp1,pp2,pp3,pp4,pp5,pp6,pp7,pp8,CL0,CL1,CL2,CL3,CL4,CL5".split(',')]

    player: Player
    camera: Camera

    def __init__(self):
        self.is_menu_stage = False
        self.t = 0

    def new(self, all_sprite, res, n_stage='1'):
        mixer.stop()
        res["musics"]["Stage1Msc"].play(loops=-1)

        currentStage = res["levels"][f"stage_{n_stage}"]
        self.tile_width = len(currentStage['0'])
        self.tile_height = len(currentStage)
        size_cam = [self.tile_width * 16,self.tile_height * 16]

        # Load camera
        self.camera = Camera([size_cam[0],size_cam[1]])

        # Load maps
        pinkColorKey = [(252,152,56), (252,188,176)]
        with open(os.path.join("res/", "indexSheetImages.json")) as f:
            locSheet = json.load(f)

        for lgn in range(0,len(currentStage)):
            for target,tile in enumerate(currentStage[str(lgn)]):
                if tile is not None:
                    x, y = (target * 16,lgn * 16)
                    if tile[0] in self.allTiles:
                        indexImg = locSheet[tile[0] if tile[0].count("pp") == 0 else tile[0].replace("pp", "pg")]
                        # Floor =-------------------
                        if tile[0].count("fa") >= 1:
                            Floor(all_sprite, res["tiles"]["floorsPlatformSheet"], [x, y], indexImg)
                        # Platform =----------------
                        if tile[0].count("pg") >= 1:    # Green
                            Platform(all_sprite, [res["tiles"]["floorsPlatformSheet"], res["tiles"]["shadowSheet"]], [x, y], indexImg)
                        if tile[0].count("pp") >= 1:    # Pink
                            Platform(all_sprite, [res["tiles"]["floorsPlatformSheet"], res["tiles"]["shadowSheet"]], [x, y], indexImg, pinkColorKey)
                        # Decors =------------------
                        if tile[0].count("CL") >= 1:
                            Cloud(all_sprite, res["tiles"]["cloudSheet"], [x,y], indexImg)
                    # Interaction block =--------
                    if tile[0] in ["LMR", "LTN"]:
                        LootBlock(all_sprite, [res["tiles"]["lootBlockSheet"], res["entities"]["MushroomSheet"]], [x, y], ("mushroom", "red") if tile[0] == "LMR" else (None, None))
                    if tile[0] == "VGE":
                        Vegetable(all_sprite, res["tiles"]["vegetationSheet"], [x, y])
                    # Entity =----------
                    if tile[0] == "GOB":
                        Goomba(self, res["entities"]["goomba"], [x, y])
                    if tile[0] == "KOP":
                        Koopa(self, res["entities"]["koopa"], [x, y])
                    if tile[0] == "COS":
                        Coin(all_sprite, res["tiles"]["coinSheet"], [x, y])
                    if tile[0] == "PLY":
                        self.player = Player(all_sprite, [res["entities"]["player"], res["tiles"]["pointsSheet"]], [x, y])
                        self.player.where = 'World'
        self.is_menu_stage = True
        return self.player

    def updates(self, dt, keys_pressed, all_sprites):
        self.player.keys = keys_pressed
        hit_list = sprite.spritecollide(self.player, all_sprites, False)
        for target in hit_list:
            self.player.collide_test(target)
        all_sprites.update(dt)
        self.camera.update(self.player)
