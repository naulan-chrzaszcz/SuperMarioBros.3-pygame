"""
    Scene n°1:
        - Manage animation of screen title
"""



class Scene1( object ):

    def __init__( self, sheet ):

        self.step = [ True, False, False, False, False, False, False ]
        self.finish = False

        self.sheet = sheet

        self.color = ( 0, 0, 0 )

        self.curtain_y = 0
        self.t_ = 0
        self.x = 0
        self.t = 0


    def start( self, surface, dt ):
        surface.fill(self.color)

        # ### --= SWITCH =-- ###
        # one step (Draw curtain)
        # Active two step (Curtain slide up)
        if int(self.t) == 15:
            self.step[1] = True
        # Active three step (Set static curtain)
        elif int(self.t) == 22:
            self.step[0] = False
            self.step[1] = False
            self.step[2] = True
        # Active four step (Title slide)
        elif int(self.t) == 25:
            self.step[3] = True
        # Active five step (Change the background color and apply final title with decors)
        elif int(self.t) == 31:
            self.step[4] = True
        # Finish
        elif int(self.t) == 35:
            self.step[0] = False
            self.step[1] = False
            self.step[2] = False
            self.step[3] = False
            self.step[4] = False
            self.step[5] = True
        self.t += (0.1 * dt)
        # ### ------------- ###

        if self.finish != 1:
            # Floor
            surface.blit(self.sheet.subsurface(( 0, 188 ), ( 256, 37 )), ( 0, surface.get_height() - 37 ))
            surface.blit(self.sheet.subsurface(( 0, 188 ), ( 256, 37 )), ( 256, surface.get_height() - 37 ))
            if self.step[0]:
                # Curtain
                surface.blit(self.sheet.subsurface(( 0, 0 ), ( 256, 35 )), ( 0, -2 - self.curtain_y ))
                surface.blit(self.sheet.subsurface(( 0, 0 ), ( 256, 35 )), ( 256, -2 - self.curtain_y ))
                surface.blit(self.sheet.subsurface(( 0, 0 ), ( 256, 187 )), ( 0, ( surface.get_height() - 221 ) - self.curtain_y ))
                surface.blit(self.sheet.subsurface(( 0, 0 ), ( 256, 187 )), ( 256, ( surface.get_height() - 221 ) - self.curtain_y ))

                # Curtain slide up
                self.curtain_y += (2.5 * dt) if self.step[1] else 0

            elif self.step[2]:
                # Shadow Curtain
                surface.blit(self.sheet.subsurface(( 257, 0 ), (16, 187)), (-11, (surface.get_height() - 214) - self.curtain_y))
                surface.blit(self.sheet.subsurface(( 257, 0 ), (256, 187)), (5, (surface.get_height() - 214) - self.curtain_y))
                surface.blit(self.sheet.subsurface(( 257, 0 ), (256, 187)), (256, (surface.get_height() - 214) - self.curtain_y))
                # Curtain
                surface.blit(self.sheet.subsurface((0, 0), (256, 35)), (0, -2 - self.curtain_y))
                surface.blit(self.sheet.subsurface((0, 0), (256, 35)), (256, -2 - self.curtain_y))
                surface.blit(self.sheet.subsurface((0, 0), (256, 187)), (0, (surface.get_height() - 221) - self.curtain_y))
                surface.blit(self.sheet.subsurface((0, 0), (256, 187)), (256, (surface.get_height() - 221) - self.curtain_y))

                # Title slide horizontal
                if self.step[ 3 ]:
                    self.x = surface.get_width() - self.t_**2
                    surface.blit( self.sheet.subsurface( (0, 226), (179, 72) ), (self.x, surface.get_height()/5) )
                    self.t_ += (0.3*dt) if int( self.x ) >= surface.get_width()/3.2 else 0

                    if self.step[ 4 ]:
                        # Change color background
                        self.color = (255, 219, 161)
                        # Blit "3" number
                        surface.blit( self.sheet.subsurface( (180, 226), (42, 41) ), (self.x + 72, surface.get_height()/4 + 62) )
                        # Draw decors
                        surface.blit( self.sheet.subsurface( (180, 268), (32, 16) ), (self.x - 22, surface.get_height()/4 - 12) )
                        surface.blit( self.sheet.subsurface( (180, 285), (16, 8) ), (self.x + 185, surface.get_height()/4 + 22) )
                        surface.blit( self.sheet.subsurface( (257, 188), (64, 64) ), (0, surface.get_height() - 101) )
                        surface.blit( self.sheet.subsurface( (322, 188), (63, 93) ), (surface.get_width() - 63, surface.get_height() - 133) )

            self.finish = True if self.step[5] else False
