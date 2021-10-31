"""
    Scene n°0:
        - Manage intro screen
"""
from pygame.transform import ( rotate )



class Scene0( object ):

    def __init__( self, sheet, sfx, event ):

        self.step = [ True, True, False, False, False ]
        self.event = event
        self.finish = False

        self.background = sheet["introBG"]
        self.beetle = sheet["beetle"]
        self.title = sheet["titleCHRZSheet"]
        self.title_y = 0
        self.alpha = 0
        self.sfx = sfx

        self.frame = 0
        self.t = 0


    def start( self, surface, dt ):
        surface.fill( (0, 0, 0) )

        if int( self.t ) == 0:
            self.sfx.play( loops=0 )
            self.t = 1
        elif int( self.t ) == 100:
            self.step[ 0 ] = False
            self.step[ 2 ] = False
            self.step[ 3 ] = True
        elif int( self.t ) == 200:
            self.step[ 4 ] = True
            self.step[ 0 ] = False
            self.step[ 1 ] = False
            self.step[ 2 ] = True
        self.frame += ( 1*dt )
        self.t += ( 1*dt )

        self.background.set_alpha( self.alpha )
        surface.blit( self.background, (0, 0) )
        surface.blit( rotate( self.beetle, 35 ), (surface.get_width() - 200, surface.get_height() - 200) )

        self.alpha += ( 5*dt ) if self.step[ 0 ] else 0
        if self.step[ 1 ]:
            surface.blit( self.title.subsurface( (int( self.frame%3 )*180, self.title_y), (180, 72) ) if self.title_y < (72*6) else self.title.subsurface( (2*180, 7*72), (180, 72) ), (surface.get_width()/4, surface.get_height()/3.2) )
            if int(self.frame) == 0:
                self.title_y += 72
        self.alpha -= ( 5*dt ) if self.step[ 3 ] else 0
        self.finish = True if self.step[ 4 ] else False
