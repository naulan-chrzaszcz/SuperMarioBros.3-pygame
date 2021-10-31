"""
    Scene n°3:
        - Animate the enter in the world
"""
from pygame import (draw, Rect)


class Scene3(object):

    def __init__(self):
        self.step = [True, False, False, False, False, False, False, False, False, False, False, False, False]
        self.finish = False

        self.spiral_rect = Rect((0, 0), (0, 30))

    def start(self, surface, dt, sfx):
        if self.finish != 1:
            # First Rect
            if self.step[0]:
                sfx["enterWorld"].play(loops=0)
                self.spiral_rect.w = self.spiral_rect.w + (20 * dt)

                if self.spiral_rect.w >= surface.get_width():
                    self.spiral_rect_2 = self.spiral_rect.copy()
                    self.spiral_rect_2.left = surface.get_width() - 40
                    self.spiral_rect_2.top = self.spiral_rect.bottom
                    self.spiral_rect_2.w = 40
                    self.step[1] = True
                    self.step[0] = False

            # 2e Rect
            elif self.step[1]:
                self.spiral_rect_2.h = self.spiral_rect_2.h + (22 * dt)

                if self.spiral_rect_2.h >= surface.get_height():
                    self.spiral_rect_3 = self.spiral_rect.copy()
                    self.spiral_rect_3.bottom = 240
                    self.spiral_rect_3.left = self.spiral_rect_2.right
                    self.step[2] = True
                    self.step[1] = False

            # 3e Rect
            elif self.step[2]:
                self.spiral_rect_3.x = self.spiral_rect_3.x - (24 * dt)

                if self.spiral_rect_3.x <= 0:
                    self.spiral_rect_4 = self.spiral_rect_2.copy()
                    self.spiral_rect_4.x = 0
                    self.spiral_rect_4.y = self.spiral_rect_3.top
                    self.step[3] = True
                    self.step[2] = False

            # 4e Rect
            elif self.step[3]:
                self.spiral_rect_4.y = self.spiral_rect_4.y - (26 * dt)

                if self.spiral_rect_4.y <= 0:
                    self.spiral_rect_5 = self.spiral_rect.copy()
                    self.spiral_rect_5.top = self.spiral_rect.bottom
                    self.spiral_rect_5.x = self.spiral_rect_5.x - surface.get_width()
                    self.step[4] = True
                    self.step[3] = False

            # 5e Rect
            elif self.step[4]:
                self.spiral_rect_5.x = self.spiral_rect_5.x + (28 * dt)

                if self.spiral_rect_5.right >= self.spiral_rect_2.left:
                    self.spiral_rect_6 = self.spiral_rect_2.copy()
                    self.spiral_rect_6.y = -self.spiral_rect_2.h
                    self.spiral_rect_6.right = self.spiral_rect_2.x
                    self.step[5] = True
                    self.step[4] = False

            # 6e Rect
            elif self.step[5]:
                self.spiral_rect_6.y = self.spiral_rect_6.y + (30 * dt)

                if self.spiral_rect_6.bottom >= self.spiral_rect_3.top:
                    self.spiral_rect_7 = self.spiral_rect_3.copy()
                    self.spiral_rect_7.x = surface.get_width()
                    self.spiral_rect_7.y = self.spiral_rect_3.y - 30
                    self.step[6] = True
                    self.step[5] = False

            # 7e Rect
            elif self.step[6]:
                self.spiral_rect_7.x = self.spiral_rect_7.x - (32 * dt)

                if self.spiral_rect_4.right >= self.spiral_rect_7.left:
                    self.spiral_rect_8 = self.spiral_rect_2.copy()
                    self.spiral_rect_8.left = self.spiral_rect_4.right
                    self.step[7] = True
                    self.step[6] = False

            # 8e Rect
            elif self.step[7]:
                self.spiral_rect_8.y = self.spiral_rect_8.y - (34 * dt)

                if self.spiral_rect_8.y >= 0:
                    self.spiral_rect_9 = self.spiral_rect.copy()
                    self.spiral_rect_9.top = self.spiral_rect_5.bottom
                    self.spiral_rect_9.right = self.spiral_rect_5.left
                    self.step[8] = True
                    self.step[7] = False

            # 9e Rect
            elif self.step[8]:
                self.spiral_rect_9.x = self.spiral_rect_9.x + (36 * dt)

                if self.spiral_rect_9.right >= self.spiral_rect_2.left:
                    self.spiral_rect_10 = self.spiral_rect_2.copy()
                    self.spiral_rect_10.left = self.spiral_rect_5.right
                    self.spiral_rect_10.x = 336
                    self.step[9] = True
                    self.step[8] = False

            # 10e Rect
            elif self.step[9]:
                self.spiral_rect_10.y = self.spiral_rect_10.y + (36 * dt)

                if self.spiral_rect_10.bottom >= self.spiral_rect_3.top:
                    self.spiral_rect_11 = self.spiral_rect_9.copy()
                    self.spiral_rect_11.y = surface.get_width() * 2
                    self.spiral_rect_11.bottom = self.spiral_rect_7.top
                    self.step[10] = True
                    self.step[9] = False

            # 11e Rect
            elif self.step[10]:
                self.spiral_rect_11.x = self.spiral_rect_11.x - (38 * dt)

                if self.spiral_rect_11.bottom >= self.spiral_rect_4.top:
                    self.step[11] = True
                    self.step[10] = False

            self.finish = True if self.step[11] else False

        try:
            draw.rect(surface, (0, 0, 0), self.spiral_rect)
            draw.rect(surface, (0, 0, 0), self.spiral_rect_2)
            draw.rect(surface, (0, 0, 0), self.spiral_rect_3)
            draw.rect(surface, (0, 0, 0), self.spiral_rect_4)
            draw.rect(surface, (0, 0, 0), self.spiral_rect_5)
            draw.rect(surface, (0, 0, 0), self.spiral_rect_6)
            draw.rect(surface, (0, 0, 0), self.spiral_rect_7)
            draw.rect(surface, (0, 0, 0), self.spiral_rect_8)
            draw.rect(surface, (0, 0, 0), self.spiral_rect_9)
            draw.rect(surface, (0, 0, 0), self.spiral_rect_10)
            draw.rect(surface, (0, 0, 0), self.spiral_rect_11)
        except AttributeError:
            pass
