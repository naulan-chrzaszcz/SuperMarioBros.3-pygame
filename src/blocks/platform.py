from pygame.sprite import ( Sprite )
from pygame import ( Surface )
from pygame.transform import ( flip )



class Platform( Sprite ):

    def __init__( self, group_sprite, sheet, position, offset, palette=None ):
        Sprite.__init__( self, group_sprite )

        # ### LIST VARIABLES ###
        self.offset_img = offset
        self.id = 'platforms'

        # Load image
        self.image = sheet[ 0 ].subsurface( (offset[ 0 ]*16, offset[ 1 ]*16), (16, 16) )

        if palette is not None:
            self.image = self.palette_swap( self.image, (0, 168, 0), palette[ 0 ] )
            self.image = self.palette_swap( self.image, (76, 220, 72), palette[ 1 ] )
            self.image.set_colorkey( (255, 174, 201) )

        if any([ offset[ 0 ] == 5, offset[ 0 ] == 2, offset[ 0 ] == 3 ]):
            self.shadow_img = sheet[ 1 ]

        # ### RECT VARIABLES ###
        self.rect = self.image.get_rect()
        self.rect.x = position[ 0 ]
        self.rect.y = position[ 1 ]


    def palette_swap( self, surf, old_c, new_c ):
        img_copy = Surface( self.image.get_size() )
        img_copy.fill( new_c )
        surf.set_colorkey( old_c )
        img_copy.blit( surf, (0, 0) )
        return img_copy


    def apply_shadow( self, surface, camera ):
        surface.blit( self.shadow_img.subsurface( (0, 0), (16, 16) ), (camera.apply( self, 16 )) )                              if self.offset_img[ 0 ] == 2 else 0
        surface.blit( self.shadow_img.subsurface( (17, 0), (16, 16) ), (camera.apply( self, 16 )) )                             if any([ self.offset_img[ 0 ] == 5, self.offset_img[ 0 ] == 3 ]) else 0
        surface.blit( flip( self.shadow_img.subsurface( (0, 0), (16, 16) ), False, True ), (camera.apply( self, 16, 16 )) )     if self.offset_img[ 0 ] == 3 else 0
