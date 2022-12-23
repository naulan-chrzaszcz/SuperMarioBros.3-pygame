from pygame.sprite import ( Sprite )



class Coin( Sprite ):

    def __init__( self, group_sprite, sheet, position, animation_speed=float( .1 ) ):
        Sprite.__init__( self, group_sprite )

        # ### STRING VARIABLES ###
        self.state = 'not_pickup'
        self.id = 'coin'

        # ### INT/FLOAT VARIABLES ###
        self.animation_speed = animation_speed
        self.frame = 0
        self.step = 0
        self.dt = 0

        self.sheet = sheet
        self.animation()

        # ### RECT VARIABLES ###
        self.rect = self.image.get_rect()
        self.rect.x = position[ 0 ]
        self.rect.y = position[ 1 ]
        self.y = position[ 1 ]


    def animation( self ):
        if self.state == 'not_pickup':
            self.image = self.sheet.subsurface( (int( self.frame%5 )*16, 0), (16, 16) )
            self.frame += (self.animation_speed*self.dt)
        elif self.state == 'pickup':
            if self.step == 0:
                # self.sfx.play(loops=0)
                self.step += 1
            elif self.step == 1:
                self.kill()


    def kill( self ):
        # self.sfx.play(loops=0)
        pass


    def update( self, dt ):
        self.dt = dt
        self.animation()
