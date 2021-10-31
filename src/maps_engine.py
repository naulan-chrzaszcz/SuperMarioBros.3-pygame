import json
import os

from pygame import Rect,sprite,mixer

from src.entitys.vegetable import Vegetable
from src.blocks.lootBlock import LootBlock
from src.blocks.platform import Platform
from src.entitys.goomba import Goomba
from src.entitys.player import Player
from src.entitys.koopa import Koopa
from src.entitys.cloud import Cloud
from src.blocks.floor import Floor
from src.entitys.coin import Coin


class Camera(object):

    def __init__(self,size):
        # ### INT/FLOAT VARIABLES ###
        self.width = size[0]
        self.height = size[1]

        # ### RECT VARIABLES ###
        self.rect = Rect(0,0,size[0],size[1])

        # ### FUNCTION VARIABLES ###
        # apply() -> Set a new value for entity (or image) according to the position of the camera
        self.apply = lambda entity,add_x=0,add_y=0: entity.rect.move((self.rect.topleft[0] + add_x),(self.rect.topleft[1] + add_y))
        self.apply_rect = lambda rect: rect.move(self.rect.topleft)

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
    player: Player
    camera: Camera

    def __init__(self):
        self.all_sprites = sprite.LayeredUpdates()

        self.is_menu_stage = False
        self.t = 0

        self.platforms = []
        self.lootBlocks = []
        self.floors = []
        self.entity = []
        self.coins = []
        self.decors = []

    def new(self, res, n_stage='1'):
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
                    if tile[0] in ["fa0","fa1","fa2","fa3","fa4","fa5","pg0","pg1","pg2","pg3","pg4","pg5","pg6","pg7","pg8","pp0","pp1","pp2","pp3","pp4","pp5","pp6","pp7","pp8","CL0","CL1","CL2","CL3","CL4","CL5"]:
                        indexImg = locSheet[tile[0] if tile[0].count("pp") == 0 else tile[0].replace("pp", "pg")]
                        # Floor =-------------------
                        if tile[0].count("fa") >= 1:
                            self.floors.append(Floor(self.all_sprites, res["tiles"]["floorsPlatformSheet"], [x, y], indexImg))
                        # Platform =----------------
                        if tile[0].count("pg") >= 1:    # Green
                            self.platforms.append(Platform(self.all_sprites, [res["tiles"]["floorsPlatformSheet"], res["tiles"]["shadowSheet"]], [x, y], indexImg))
                        if tile[0].count("pp") >= 1:    # Pink
                            self.platforms.append(Platform(self.all_sprites, [res["tiles"]["floorsPlatformSheet"], res["tiles"]["shadowSheet"]], [x, y], indexImg, pinkColorKey))
                        # Decors =------------------------------------------------------------------------------------------------------
                        if tile[0].count("CL") >= 1:
                            self.decors.append(Cloud(self.all_sprites, res["tiles"]["cloudSheet"], [x,y], indexImg))
                    # Interaction block =--------
                    if tile[0] in ["LMR", "LTN"]:
                        self.lootBlocks.append(LootBlock(self.all_sprites, [res["tiles"]["lootBlockSheet"], res["entities"]["MushroomSheet"]], [x, y], ("mushroom", "red") if tile[0] == "LMR" else (None, None)))
                    if tile[0] == "VGE":
                        self.decors.append(Vegetable(self.all_sprites, res["tiles"]["vegetationSheet"], [x, y]))
                    # Entity =----------
                    if tile[0] == "GOB":
                        self.entity.append(Goomba(self, res["entities"]["goomba"], [x, y]))
                    if tile[0] == "KOP":
                        self.entity.append(Koopa(self, res["entities"]["koopa"], [x, y]))
                    if tile[0] == "COS":
                        self.entity.append(Coin(self.all_sprites, res["tiles"]["coinSheet"], [x, y]))
                    if tile[0] == "PLY":
                        self.player = Player(self, [res["entities"]["player"], res["tiles"]["pointsSheet"]], [x, y])
                        self.player.where = 'World'
        self.is_menu_stage = True

    def draw(self,surface):
        surface.fill((156,252,240))
        for target in reversed(self.platforms):
            if all([self.camera.rect.left + 16 >= -target.rect.left,(self.tile_width - self.camera.rect.left + 390) >= target.rect.left]):
                surface.blit(target.image,self.camera.apply(target))
                target.apply_shadow(surface,self.camera) if any([target.offset_img[0] == 5,target.offset_img[0] == 2,target.offset_img[0] == 3]) else None
        for target in self.floors:
            surface.blit(target.image,self.camera.apply(target)) if all([self.camera.rect.left + 16 >= -target.rect.left,(self.tile_width - self.camera.rect.left + 390) >= target.rect.left]) else None
        for target in self.lootBlocks:
            if len(target.mushrooms) != 0:
                for mush in target.mushrooms:
                    surface.blit(mush.image,self.camera.apply(mush)) if all([self.camera.rect.left + 16 >= -mush.rect.left,(self.tile_width - self.camera.rect.left + 390) >= mush.rect.left]) else None
            surface.blit(target.image,self.camera.apply(target)) if all([self.camera.rect.left + 16 >= -target.rect.left,(self.tile_width - self.camera.rect.left + 390) >= target.rect.left]) else None
        for target in self.decors:
            surface.blit(target.image,self.camera.apply(target)) if all([self.camera.rect.left + 16 >= -target.rect.left,(self.tile_width - self.camera.rect.left + 390) >= target.rect.left]) else None
        for target in self.entity:
            self.entity.remove(target) if target.step == 1 else None
            surface.blit(target.image,self.camera.apply(target)) if all([self.camera.rect.left + 16 >= -target.rect.left,(self.tile_width - self.camera.rect.left + 390) >= target.rect.left]) else None
        surface.blit(self.player.image,self.camera.apply(self.player))

    def updates(self,dt,keys_pressed):
        self.player.keys = keys_pressed
        hit_list = sprite.spritecollide(self.player,self.all_sprites,False)
        for target in hit_list:
            self.player.collide_test(target)
        self.all_sprites.update(dt)
        self.camera.update(self.player)
