from src.blocks.block import Block
from src.blocks.type_of_block import TypeOfBlock
from src.constantes import TILE_WIDTH
from src.entitys.entity import Entity


class Platform(Block):

    def __init__(self, game, group_sprite, type_of_block, position, palette=None):
        Block.__init__(self, game, group_sprite, type_of_block)

        self.id = 'platforms'

        # Load image
        self.image = game.res["tiles"]["floorsPlatformSheet"].subsurface((offset[0] * 16, offset[1] * 16), (16, 16))

        if palette is not None:
            self.image = Entity.palette_swap(self.image, (0, 168, 0), palette[0])
            self.image = Entity.palette_swap(self.image, (76, 220, 72), palette[1])
            self.image.set_colorkey((255, 174, 201))

        if any([offset[0] == 5, offset[0] == 2, offset[0] == 3]):
            self.shadow_img = sheet[1]

        # ### RECT VARIABLES ###
        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]

    def update(self, *args, **kwargs) -> None:
        maps = kwargs["maps"]
        display = kwargs["display"]

        if maps.camera.rect.left + 16 >= -self.rect.lef and (TILE_WIDTH - maps.camera.rect.left + 390) >= self.rect.left:
            display.blit(self.image, maps.camera.apply(self))
            if any([TypeOfBlock.is_corner_right_top(self.type_of_block),
                    TypeOfBlock.is_left(self.type_of_block),
                    TypeOfBlock.is_bottom(self.type_of_block)]):
                Block.apply_shadow(self, display, maps.camera)
