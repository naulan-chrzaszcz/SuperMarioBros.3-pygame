from abc import abstractmethod

from pygame import Surface
from pygame.sprite import Sprite
from pygame.transform import flip

from src.blocks.type_of_block import TypeOfBlock
from src.game import Game
from src.maps_engine import Camera


class Block(Sprite):
    type_of_block: TypeOfBlock
    game: Game

    def __init__(self, game, group_sprite, type_of_block):
        Sprite.__init__(self, group_sprite)
        self.type_of_block = type_of_block
        self.game = game

    @staticmethod
    def apply_shadow(sprite, surface: Surface, camera: Camera):
        if TypeOfBlock.is_corner_right_top(sprite.type_of_block):
            surface.blit(sprite.shadow_img.subsurface((0, 0), (16, 16)), (camera.apply(sprite, 16)))
        if TypeOfBlock.is_left(sprite.type_of_block) or TypeOfBlock.is_bottom(sprite.type_of_block):
            surface.blit(sprite.shadow_img.subsurface((17, 0), (16, 16)), (camera.apply(sprite, 16)))
        if TypeOfBlock.is_corner_left_bottom(sprite.type_of_block):
            surface.blit(flip(sprite.shadow_img.subsurface((0, 0), (16, 16)), False, True), camera.apply(sprite, 16, 16))

    @abstractmethod
    def update(self, *args, **kwargs) -> None:
        pass
