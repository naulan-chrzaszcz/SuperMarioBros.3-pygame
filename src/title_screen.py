from .scenes.scene_1 import ( Scene1 )
from pygame.locals import *
from .font import ( Font )
from math import ( sin )



class TitleScreen( object ):

    def __init__( self, sheet ):
        # Class
        self.scene = Scene1( sheet )
        self.font = Font()
        self.keys = None

        # ### BOOLEAN VARIABLES ###
        self.pass_stage_menu = False
        self.is_title = True

        # ### INT/FLOAT VARIABLES ###
        self.color = ( 0, 0, 0 )
        self.dt = .0
        self.t = 0

        # Resources
        self.sheet = sheet


    def draw( self, surface ):
        if self.scene.finish != 1:  self.scene.start( surface, self.dt )
        elif self.scene.finish:
            surface.fill( (255, 219, 161) )
            # Floor
            surface.blit( self.sheet.subsurface( (0, 188), (256, 37) ), (0, surface.get_height() - 37) )
            surface.blit( self.sheet.subsurface( (0, 188), (256, 37) ), (256, surface.get_height() - 37) )
            # Shadow Curtain
            surface.blit( self.sheet.subsurface( (257, 0), (16, 187) ), (-11, (surface.get_height() - 214) - self.scene.curtain_y) )
            surface.blit( self.sheet.subsurface( (257, 0), (256, 187) ), (5, (surface.get_height() - 214) - self.scene.curtain_y) )
            surface.blit( self.sheet.subsurface( (257, 0), (256, 187) ), (256, (surface.get_height() - 214) - self.scene.curtain_y) )
            # Curtain
            surface.blit( self.sheet.subsurface( (0, 0), (256, 35) ), (0, -2 - self.scene.curtain_y) )
            surface.blit( self.sheet.subsurface( (0, 0), (256, 35) ), (256, -2 - self.scene.curtain_y) )
            surface.blit( self.sheet.subsurface( (0, 0), (256, 187) ), (0, (surface.get_height() - 221) - self.scene.curtain_y) )
            surface.blit( self.sheet.subsurface( (0, 0), (256, 187) ), (256, (surface.get_height() - 221) - self.scene.curtain_y) )
            # Title
            surface.blit( self.sheet.subsurface( (0, 226), (179, 72) ), (self.scene.x, surface.get_height()/5) )
            # Blit "3" number
            surface.blit( self.sheet.subsurface( (180, 226), (42, 41) ), (self.scene.x + 72, surface.get_height()/4 + 62) )
            # Draw decors
            surface.blit( self.sheet.subsurface( (180, 268), (32, 16) ), (self.scene.x - 22, (surface.get_height()/4 - 12) + sin( self.t )*5) )
            surface.blit( self.sheet.subsurface( (180, 285), (16, 8) ), (self.scene.x + 185, (surface.get_height()/4 + 22) + sin( self.t - 1 )*3.5) )
            surface.blit( self.sheet.subsurface( (257, 188), (64, 64) ), (0, surface.get_height() - 101) )
            surface.blit( self.sheet.subsurface( (322, 188), (63, 93) ), (surface.get_width() - 63, surface.get_height() - 133) )
            # Text
            self.font.draw_msg( surface, [ (surface.get_width()/2.6) + sin( self.t ), surface.get_height()/4 + 105 ], 'P' )
            self.font.draw_msg( surface, [ ((surface.get_width()/2.6) + sin( self.t - 1 )*2) + 7, surface.get_height()/4 + 105 ], 'R' )
            self.font.draw_msg( surface, [ ((surface.get_width()/2.6) + sin( self.t - 2 )*2) + (7*2), surface.get_height()/4 + 105 ], 'E' )
            self.font.draw_msg( surface, [ ((surface.get_width()/2.6) + sin( self.t - 3 )*2) + (7*3), surface.get_height()/4 + 105 ], 'S' )
            self.font.draw_msg( surface, [ ((surface.get_width()/2.6) + sin( self.t - 4 )*2) + (7*4), surface.get_height()/4 + 105 ], 'S' )
            self.font.draw_msg( surface, [ ((surface.get_width()/2.6) + sin( self.t - 5 )*2) + (7*5) + 5, surface.get_height()/4 + 105 ], 'A' )
            self.font.draw_msg( surface, [ ((surface.get_width()/2.6) + sin( self.t - 6 )*2) + (7*6) + 10, surface.get_height()/4 + 105 ], 'T' )
            self.font.draw_msg( surface, [ ((surface.get_width()/2.6) + sin( self.t - 7 )*2) + (7*7) + 10, surface.get_height()/4 + 105 ], 'O' )
            self.font.draw_msg( surface, [ ((surface.get_width()/2.6) + sin( self.t - 8 )*2) + (7*8) + 15, surface.get_height()/4 + 105 ], 'S' )
            self.font.draw_msg( surface, [ ((surface.get_width()/2.6) + sin( self.t - 9 )*2) + (7*9) + 15, surface.get_height()/4 + 105 ], 'T' )
            self.font.draw_msg( surface, [ ((surface.get_width()/2.6) + sin( self.t - 10 )*2) + (7*10) + 15, surface.get_height()/4 + 105 ], 'A' )
            self.font.draw_msg( surface, [ ((surface.get_width()/2.6) + sin( self.t - 11 )*2) + (7*11) + 15, surface.get_height()/4 + 105 ], 'R' )
            self.font.draw_msg( surface, [ ((surface.get_width()/2.6) + sin( self.t - 12 )*2) + (7*12) + 15, surface.get_height()/4 + 105 ], 'T' )

            self.t += (.05*self.dt)


    def updates( self, dt, keys_pressed ):
        self.keys = keys_pressed
        self.dt = dt

        if self.keys[ f'{K_a}' ]:
            self.pass_stage_menu = True
            self.is_title = False
