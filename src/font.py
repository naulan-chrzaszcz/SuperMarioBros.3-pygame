from pygame import ( image, mask, font )



class Font( object ):

    def __init__( self ):
        self.letters = [ [ 'A', 0 ], [ 'B', 1 ], [ 'C', 2 ], [ 'D', 3 ], [ 'E', 4 ], [ 'F', 5 ], [ 'G', 6 ], [ 'H', 7 ], [ 'I', 8 ], [ 'J', 9 ], [ 'K', 10 ], [ 'L', 11 ], [ 'M', 12 ], [ 'N', 13 ], [ 'O', 14 ], [ 'P', 15 ], [ 'Q', 16 ], [ 'R', 17 ], [ 'S', 18 ], [ 'T', 19 ], [ 'U', 20 ], [ 'V', 21 ], [ 'W', 22 ], [ 'X', 23 ], [ 'Y', 24 ], [ 'Z', 25 ], [ '0', 26 ], [ '1', 27 ], [ '2', 28 ], [ '3', 29 ], [ '4', 30 ], [ '5', 31 ], [ '6', 32 ], [ '7', 33 ], [ '8', 34 ], [ '9', 35 ] ]
        self.font = font.Font( r'res/font.ttf', 16 )
        self.custom_font = image.load( r'res/sheets/custom_font.png' )
        self.custom_font.set_colorkey( (255, 174, 201) )


    @staticmethod
    def outline( surface, img, loc ):
        masks = mask.from_surface( img )
        mask_surf = masks.to_surface( setcolor=(1, 1, 1, 255) )
        mask_surf.set_colorkey( (0, 0, 0) )
        surface.blit( mask_surf, (loc[ 0 ] - 1, loc[ 1 ]) )
        surface.blit( mask_surf, (loc[ 0 ] + 1, loc[ 1 ]) )
        surface.blit( mask_surf, (loc[ 0 ], loc[ 1 ] - 1) )
        surface.blit( mask_surf, (loc[ 0 ], loc[ 1 ] + 1) )


    def draw_msg( self, surface, position, messages, score=None ):
        for char in reversed( messages ):
            for n in range( len( self.letters ) ):
                if char == self.letters[ n ][ 0 ]:
                    surface.blit( self.custom_font.subsurface( (self.letters[ n ][ 1 ]*8, 0), (8, 8) ), (position[ 0 ], position[ 1 ]) )
                    position[ 0 ] -= 7
                elif any( [ char == '_', char == ' ', char == '.' ] ):
                    position[ 0 ] -= 4

        if score:
            for fill in range( 9 - len( messages ) ):
                x__ = position[ 0 ] - (7*fill if fill > 0 else 0)
                surface.blit( self.custom_font.subsurface( self.letters[ 25 ][ 1 ]*8, 0, 8, 8 ), (x__, position[ 1 ]) )
