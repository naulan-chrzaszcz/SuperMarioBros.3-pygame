from pygame.time import (Clock)
from .font import (Font)
import time


class Fps(object):

    def __init__(self):
        # ### CLASS CALL VARIABLE ###
        self.prev_time = time.time()
        self.clock = Clock()
        self.font = Font()

        # ### BOOLEAN VARIABLES ###
        self.benchmark = True

        # ### LIST VARIABLES ###
        self.list_fps = []
        self.get()

        # INT/FLOAT VARIABLES ###
        self.t = 0
        self.dt = self.manage(fps=120)
        self.avg = sum(self.list_fps) / len(self.list_fps)
        self.max = max(self.list_fps)
        self.min = min(self.list_fps)

    def manage(self,fps):
        self.clock.tick(fps)
        self.dt = float(time.time() - self.prev_time)
        self.prev_time = time.time()
        return self.dt * 60

    def average(self):
        if self.list_fps.count(.0) >= 1:
            self.list_fps.clear()
        else:
            self.avg = round(sum(self.list_fps) / len(self.list_fps))
            self.max = round(max(self.list_fps))
            self.min = round(min(self.list_fps))
            return self.avg,self.max,self.min

    def get(self):
        self.list_fps.append(self.clock.get_fps())
        return round(self.list_fps[len(self.list_fps) - 1])

    def draw(self,surface):
        msg = [self.font.font.render(f'{self.get()} Fps',0,(255,255,255)),self.font.font.render(f'avg:  {self.avg} Fps',0,(255,255,255)),self.font.font.render(f'max: {self.max} Fps',0,(255,255,255)),self.font.font.render(f'min: {self.min} Fps',0,(255,255,255)),self.font.font.render(f'var: {round(self.dt,3)} ms',0,(255,255,255))]
        self.font.outline(surface,msg[1],(5,5))
        self.font.outline(surface,msg[0],(5,msg[0].get_height() + 7))
        self.font.outline(surface,msg[2],(msg[0].get_width() * 2.5,5))
        self.font.outline(surface,msg[3],(msg[0].get_width() * 2.5,msg[2].get_height() * 1.5))
        self.font.outline(surface,msg[4],(5,msg[1].get_height() * 2.5))
        surface.blit(msg[1],(5,5))
        surface.blit(msg[0],(5,msg[0].get_height() + 7))
        surface.blit(msg[2],(msg[0].get_width() * 2.5,5))
        surface.blit(msg[3],(msg[0].get_width() * 2.5,msg[2].get_height() * 1.5))
        surface.blit(msg[4],(5,msg[1].get_height() * 2.5))
