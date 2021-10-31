from pygame.sprite import ( Sprite )
from random import ( choice )



class Cloud( Sprite ):

    def __init__( self, group_sprite, sheet, position, offset ):
        Sprite.__init__( self, group_sprite )

        self.id = 'cloud'

        self.offset = offset
        self.frame = 0
        self.dt = .0
        self.var = choice( (.05, .1, .025, .075) )

        self.sheet = sheet
        self.image = sheet.subsurface( (offset[ 0 ]*16, offset[ 1 ]*16), (16, 16) )

        self.rect = self.image.get_rect()
        self.rect.x = position[ 0 ]
        self.rect.y = position[ 1 ]


    def animation( self ):
        if self.offset[ 0 ] == 1 and self.offset[ 1 ] == 0:
            self.frame += (self.var*self.dt)
            self.image = self.sheet.subsurface( (48, 0), (16, 16) ) if int(self.frame%11) == 10 else self.sheet.subsurface( (16, 0), (16, 16) )


    def update(self, dt):
        self.dt = dt
        self.animation()
