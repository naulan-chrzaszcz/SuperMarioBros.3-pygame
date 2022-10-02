from math import cos,sin
from pygame import Surface

from src.font import Font


class Scene1(object):
    clock_scene: float = .1
    speed_curtain: float = 1.25
    sheet: Surface

    def __init__(self):
        self.font = Font()
        self.curtain_y = 0
        self.titleX = 0
        self.t = 0
        self.color = (0, 0, 0)

    def getBackgroundColor(self) -> tuple:
        return self.color

    def start(self, surface: Surface, dt: float) -> None:
        """ Par default -> Affiche le sol et le rideau.
            self.step[0] -> le rideau slide vers le haute
            self.step[1] -> Affiche la couleurs de l'arrière plan, l'ombre du rideau et la vegetation
            self.step[2] -> Affiche l'animation du titre vers sa position final
            self.step[3] -> Affiche "Press A to start"

        :param dt: DeltaTime """
        h = surface.get_height(); w = surface.get_width()
        
        if 36 > int(self.t) > 20:
            self.curtain_y += (self.speed_curtain * dt)

        if int(self.t) > 38:
            sinus = sin(self.t/2)
            self.color = (255,219,161)
            # Shadow Curtain
            surface.blit(self.sheet.subsurface((257,0),(16,187)),(-11,(h - 214) - self.curtain_y))
            surface.blit(self.sheet.subsurface((257,0),(256,187)),(5,(h - 214) - self.curtain_y))
            surface.blit(self.sheet.subsurface((257,0),(256,187)),(256,(h - 214) - self.curtain_y))
            # Draw decors
            surface.blit(self.sheet.subsurface((180,268),(32,16)), (w/3.5 - 22,(h/4 - 12) + sinus * 5))
            surface.blit(self.sheet.subsurface((180,285),(16,8)),(w/3.5 + 185,(h/4 + 22) + sinus * 3.5))
            surface.blit(self.sheet.subsurface((257,188),(64,64)),(0,h - 101))
            surface.blit(self.sheet.subsurface((322,188),(63,93)),(w - 63,h - 101))
        if int(self.t) > 38:
            title = self.sheet.subsurface((0,226),(179,72))
            title3 = self.sheet.subsurface((180,226),(42,41))
            surface.blit(title,((w / 2) - (title.get_width()/2), h / 5))
            surface.blit(title3, ((w / 2) - (title3.get_width()/2), (h / 5) + title.get_height()))  # Blit "3" number
            if int(self.t) > 45:
                hPressAToStart = h/4 + 105; wPressAToStart = w/2.6
                pressAtoStart = {'P': [wPressAToStart+sin(self.t), hPressAToStart], 'R': [wPressAToStart+sin(self.t-1)*2 + 7, hPressAToStart],
                                 'E': [wPressAToStart+sin(self.t-2)*2 + 7*2, hPressAToStart], 'S': [wPressAToStart+sin(self.t-3)*2 + 7*3, hPressAToStart],
                                 "S_":[wPressAToStart+sin(self.t-4)*2 + 7*4, hPressAToStart], 'A': [wPressAToStart+sin(self.t-5)*2 + 7*5+5, hPressAToStart],
                                 'T': [wPressAToStart+sin(self.t-6)*2 + 7*6+10, hPressAToStart], 'O': [wPressAToStart+sin(self.t-7)*2 + 7*7+10, hPressAToStart],
                                 "S__": [wPressAToStart+sin(self.t-8)*2 + 7*8+15, hPressAToStart],"T_": [wPressAToStart+sin(self.t - 9)*2 + 7*9+15, hPressAToStart],
                                 "A_":[wPressAToStart+sin(self.t-10)*2 + 7*10+15, hPressAToStart], "R_": [wPressAToStart+sin(self.t - 11)*2 + 7*11+15, hPressAToStart],
                                 "T__": [wPressAToStart+sin(self.t-12)*2 + 7*12+15, hPressAToStart]}
                for letter in pressAtoStart.keys():
                    loc = pressAtoStart[letter]
                    self.font.draw_msg(surface, loc, letter.replace(f'{"_"*letter.count("_")}', "") if letter.count('_') > 0 else letter)

        self.t += (self.clock_scene * dt)

