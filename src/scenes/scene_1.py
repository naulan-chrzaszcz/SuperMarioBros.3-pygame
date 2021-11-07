# coding:UTF-8
from typing import List
from pygame import Surface


class Scene1(object):
    sheet: Surface
    t: List

    def __init__(self):
        self.step = [False,False,False,False]
        self.finish = False

        self.curtain_y = 0
        self.x = 0
        self.t = [0,0,0]
        self.color = (0, 0, 0)

    def getFinish(self) -> bool:
        return self.finish

    def setFinish(self,arg):
        self.finish = arg

    def getBackgroundColor(self) -> tuple:
        return self.color

    def start(self,surface,dt) -> None:
        """ Par default -> Affiche le sol et le rideau.
            self.step[0] -> le rideau slide vers le haute
            self.step[1] -> Affiche la couleurs de l'arrière plan, l'ombre du rideau et la vegetation
            self.step[2] -> 
            self.step[3] ->

        :param dt: DeltaTime """

        match int(self.t[0]):
            case 15:
                self.step[0] = True
            case 22:
                self.step[0] = False; self.step[1] = True
            case 25:
                self.step[2] = True
            case 31:
                self.step[3] = True
            case 35:  # Finish
                self.step = [False,True,False,True]
        self.t[0] += (.1 * dt)

        if not self.finish:
            if self.step[0]:
                self.curtain_y += (2.72 * dt)
            if self.step[1]:
                self.color = (255,219,161)
                # Shadow Curtain
                surface.blit(self.sheet.subsurface((257,0),(16,187)),(-11,(surface.get_height() - 214) - self.curtain_y))
                surface.blit(self.sheet.subsurface((257,0),(256,187)),(5,(surface.get_height() - 214) - self.curtain_y))
                surface.blit(self.sheet.subsurface((257,0),(256,187)),(256,(surface.get_height() - 214) - self.curtain_y))
