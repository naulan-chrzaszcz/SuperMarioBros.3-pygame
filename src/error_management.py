from datetime import datetime
import requests, shutil, sys, json
import pygame as pg



class ErrorManagement( Exception ):

    def __init__(self):

        with open( r'res/urlFileBackup.json' ) as __url:        self.url_list = json.load( __url )
        self.all_error = []


    def popup( self ):
        pass


    def write_report( self ):
        if len( self.all_error ) != 0:
            now = datetime.now()
            with open( rf"ErrorReport_{now.strftime( '%d.%m.%Y_%H.%M.%S' )}.txt", 'w+t' ) as error_report:
                for i in range( len( self.all_error ) ):    error_report.write( self.all_error[ i ] )


    def try_load_texture( self, who, directory, mode, surface ):
        try:
            for target in self.url_list[ who ]: open( rf'{directory}' + target )
        except FileNotFoundError:
            self.all_error.append( '=------------------------------= \n' + f'File not found -> "{target}"\n' )
            # Show the file who isn't found
            surface.fill( (0, 0, 0) )
            surface.blit( pg.font.SysFont( 'arial', 16 ).render( f'File not found -> "{target}"', 0, (255, 255, 255) ), (0, 0) )
            pg.display.update()

            try:
                self.all_error.append( f'Download file on "{self.url_list[ who ][ target ]}" \n' )
                # Try connect | get file
                file = requests.get( self.url_list[ who ][ target ], stream=1 )
                surface.blit(pg.font.SysFont( 'arial', 16 ).render( f'Download file is completed -> "{target}"', 0, (255, 255, 255) ), (0, 18) )
            except requests.exceptions.ConnectionError or requests.exceptions.Timeout:
                self.all_error.append( f'Connection error on "{self.url_list[ who ][ target ]}" \nExit the game... \n' )

                # Write all error on the program
                self.write_report()

                pg.quit()
                sys.exit()

            # If download is 100% complete
            if file.status_code == 200:
                with open( rf'{directory}' + target, 'w+b' ) as f:
                    if mode == 'image':
                        file.raw.decode_content = 1
                        shutil.copyfileobj( file.raw, f )
                    elif mode == 'text':
                        f.write( file.content )
                self.all_error.append( 'Download file is completed \n' + '=------------------------------= \n' )
