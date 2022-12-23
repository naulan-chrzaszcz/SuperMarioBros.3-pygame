from pygame.sprite import Sprite


class Floor(Sprite):

    def __init__(self, group_sprite, tiles, position, offset):
        Sprite.__init__(self, group_sprite)

        # ### LIST VARIABLES ###
        self.offset_img = offset
        self.id = 'floors'

        # Load image
        self.image = tiles.subsurface( (offset[ 0 ]*16, offset[ 1 ]*16), (16, 16) )

        # ### RECT VARIABLES ###
        self.rect = self.image.get_rect()
        self.rect.x = position[ 0 ]
        self.rect.y = position[ 1 ]
