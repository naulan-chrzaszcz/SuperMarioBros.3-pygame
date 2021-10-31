from pygame.sprite import ( Sprite )
from src.entitys.mushroom import ( Mushroom )
from math import sin



class LootBlock( Sprite ):

    def __init__( self, group_sprite, sheet, position, loot ):

        self.groups = group_sprite
        Sprite.__init__( self, group_sprite )

        # ### STRING VARIABLES ###
        self.id = 'lootblock'
        self.state = 'normal'
        self.what_loot, self.color = loot

        self.mushrooms = []
        # ### INT/FLOAT VARIABLES ###
        self.frame = 0
        self.step = 0
        self.dt = 0
        self.t = 0

        self.image = sheet[ 0 ].subsurface((0, 0), (16, 16))
        self.sheet = sheet
        self.animation()

        # ### RECT VARIABLES ###
        self.rect = self.image.get_rect()
        self.rect.x = position[ 0 ]
        self.rect.y = position[ 1 ]
        self.y_init = position[ 1 ]
        self.mushroom_x = position[ 0 ]
        self.mushroom_y = position[ 1 ] + 17
        self.spawn = False


    def animation( self ):
        if self.state == 'normal':
            self.image = self.sheet[ 0 ].subsurface( (int( self.frame%4 )*16, 0), (16, 16) )
            self.frame += (.1*self.dt)
        elif self.state == 'activated':
            self.t += (.1*self.dt)
            self.image = self.sheet[ 0 ].subsurface( (4*16, 0), (16, 16) )
            if int(self.t**2) + self.y_init != self.y_init:
                self.rect.y = 10*sin(self.t) + self.y_init


    def update( self, dt ):
        self.dt = dt
        self.animation()

        if all([ self.state == 'activated', self.what_loot == 'mushroom', self.spawn is False ]):
            self.mushrooms.append(Mushroom( self.groups, self.sheet[ 1 ], [ self.mushroom_x, self.mushroom_y ], 'red' if self.color == 'red' else 'green' ))
            self.spawn = True
