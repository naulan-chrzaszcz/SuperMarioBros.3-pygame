from pygame import image, mask, font, Surface


class Font(object):
    def __init__(self):
        # It represent where a char (self.__letters[n][0]) is located in a picture (self.__letters[n][1])
        self.__letters = [['A',0],['B',1],['C',2],['D',3],['E',4],['F',5],['G',6],['H',7],['I',8],['J',9],['K',10],
                          ['L',11],['M',12],['N',13],['O',14],['P',15],['Q',16],['R',17],['S',18],['T',19],['U',20],
                          ['V',21],['W',22],['X',23],['Y',24],['Z',25],['0',26],['1',27],['2',28],['3',29],['4',30],
                          ['5',31],['6',32],['7',33],['8',34],['9',35]]
        # TODO Clean les noms des variables
        self.font = font.Font(r'res/font.ttf', 16)   # TODO <--
        self.custom_font = image.load(r'res/sheets/custom_font.png')   # TODO <--
        self.custom_font.set_colorkey((255, 174, 201))

    def get_SystemFont(self) -> font.Font:
        """ get_SystemFont() -> Font
               get the font which as been loaded by a ".ttf" file and Font class """
        return self.font

    def get_GameFont(self) -> Surface:
        return self.custom_font

    @staticmethod
    def outline(surface,img,loc):
        masks = mask.from_surface(img)
        mask_surf = masks.to_surface(setcolor=(1,1,1,255))
        mask_surf.set_colorkey((0,0,0))
        surface.blit(mask_surf,(loc[0] - 1,loc[1]))
        surface.blit(mask_surf,(loc[0] + 1,loc[1]))
        surface.blit(mask_surf,(loc[0],loc[1] - 1))
        surface.blit(mask_surf,(loc[0],loc[1] + 1))

    def draw_msg(self,surface,position,messages,score=None):
        for char in reversed(messages.upper()):
            for n in range(len(self.__letters)):
                if any([char == '_',char == ' ',char == '.']):
                    position[0] -= .1

                elif char == self.__letters[n][0]:
                    loc = (position[0], position[1])
                    surface.blit(self.custom_font.subsurface((self.__letters[n][1]*8, 0), (8, 8)), loc)
                    position[0] -= 6

        if score is not None:
            for fill in range(9 - len(messages)):
                x__ = position[0] - (7 * fill if fill > 0 else 0)
                surface.blit(self.custom_font.subsurface(self.__letters[25][1] * 8,0,8,8),(x__,position[1]))
