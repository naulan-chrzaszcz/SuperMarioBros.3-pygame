from pygame import draw, Rect
from math import cos, sin

from src.font import Font


class Scene2(object):

    def __init__(self,sheet):
        self.font = Font()

        # Resources
        self.player_sheet = sheet[0]
        self.stars_sheet = sheet[1]

        # ### INT/FLOAT VARIABLES ###
        self.item_frame_w = 152
        self.msg_frame_w = self.item_frame_w / 1.1
        self.stars_position = [0,0]
        self.multiplication = 1
        self.target = 0
        self.t_cos = 0
        self.t_sin = 0
        self.t = 0

        # ### BOOLEAN VARIABLES ###
        self.switch_multiplication = [False,False]
        self.step = [False,False,False,False]
        self.finish = False

    def start(self,surface,dt,more_info,sfx):
        # ### --= SWITCH =-- ###
        # Active one step
        if int(self.t) == 0:
            self.step[0] = True
            self.step[1] = False
            self.step[2] = False
            self.step[3] = False
        # Active two step
        elif int(self.t) == 15:
            self.step[0] = True
            self.step[1] = True
            self.step[2] = False
            self.step[3] = False
        # Active three step
        elif int(self.t) == 18:
            sfx["newWorld"].play()
            self.step[0] = False
            self.step[1] = False
            self.step[2] = True
            self.step[3] = False
        # Active four step
        elif int(self.t) == 33:
            self.step[0] = False
            self.step[1] = False
            self.step[2] = False
            self.step[3] = True
        self.t += (.1 * dt)
        if int(self.t_cos) == 0:
            self.switch_multiplication[1] = False
            self.switch_multiplication[0] = True
        elif int(self.t_cos) == 7:
            self.switch_multiplication[0] = False
            self.switch_multiplication[1] = True
        # ### -------------- ###

        if self.finish != 1:
            # ### RECT VARIABLES ###
            # item_frame = Rect((surface.get_width() / 3,surface.get_height() / 4),(self.item_frame_w,80))
            msg_frame = Rect((surface.get_width() / 2.86,surface.get_height() / 3.52),(self.msg_frame_w,item_frame.height / 1.25))

            # ### -----------== Step one with step two of the animation ==----------- ###
            if self.step[0]:
                # window
                # draw.rect(surface,(0,0,0),item_frame)
                draw.rect(surface,(175,232,226),msg_frame)

                if self.step[1] == 0:
                    # player
                    surface.blit(self.player_sheet.subsurface(32,16,16,16),(((surface.get_width() + msg_frame.w / 2) / 2.18),((surface.get_height() + msg_frame.h / 2) / 2.8)))
                    # msg
                    self.font.draw_msg(surface,[((surface.get_width() + msg_frame.w / 2) / 2.01),((surface.get_height() + msg_frame.h / 2) / 2.6)],f'{more_info[0]}')
                    self.font.draw_msg(surface,[((surface.get_width() + msg_frame.w / 2) / 2.18),((surface.get_height() + msg_frame.h / 2) / 3.8)],f'WORLD{more_info[1]}')
                    self.font.draw_msg(surface,[((surface.get_width() + msg_frame.w / 2) / 2.48),((surface.get_height() + msg_frame.h / 2) / 2.6)],f'{more_info[2]}')
                else:
                    if int(self.item_frame_w) >= 0:
                        self.item_frame_w -= (5 * dt)
                        self.msg_frame_w -= (5 * dt)

                # Outline window
                if int(self.item_frame_w) > 0:
                    draw.line(surface,(255,255,255),(msg_frame.topleft[0] - 2,msg_frame.topleft[1] - 1),(msg_frame.bottomleft[0] - 2,msg_frame.bottomleft[1]),2)
                    draw.line(surface,(255,255,255),(msg_frame.topleft[0] - 1,msg_frame.topleft[1] - 2),(msg_frame.topright[0],msg_frame.topright[1] - 2),2)
                    draw.line(surface,(255,255,255),(msg_frame.bottomleft[0] - 1,msg_frame.bottomleft[1]),(msg_frame.bottomright[0],msg_frame.bottomright[1]),2)
                    draw.line(surface,(255,255,255),(msg_frame.topright[0],msg_frame.topright[1] - 1),(msg_frame.bottomright[0],msg_frame.bottomright[1]),2)
            # ### ------------------------------------------------------------------- ###

            elif self.step[2]:
                if self.switch_multiplication[0]:
                    self.multiplication += (1.5 * dt)
                    self.target += (0.05 * dt)
                elif self.switch_multiplication[1]:
                    self.multiplication -= (1.2 * dt)
                    self.target -= (0.05 * dt)
                    if int(self.target) == -1:
                        self.target = 0
                        self.switch_multiplication[1] = False

                # Stars
                surface.blit(self.stars_sheet.subsurface((11 * int(self.target),0),(11,11)),(((cos(self.t_cos) * self.multiplication) + item_frame.left) - self.stars_position[0],(sin(self.t_sin) * self.multiplication) + item_frame.left / 1.5))
                surface.blit(self.stars_sheet.subsurface((11 * int(self.target),0),(11,11)),(((cos(self.t_cos - 5) * self.multiplication) + item_frame.left) - self.stars_position[0],(sin(self.t_sin - 5) * self.multiplication) + item_frame.left / 1.5))
                surface.blit(self.stars_sheet.subsurface((11 * int(self.target),0),(11,11)),(((cos(self.t_cos - 10) * self.multiplication) + item_frame.left) - self.stars_position[0],(sin(self.t_sin - 10) * self.multiplication) + item_frame.left / 1.5))
                surface.blit(self.stars_sheet.subsurface((11 * int(self.target),0),(11,11)),(((cos(self.t_cos - 15) * self.multiplication) + item_frame.left) - self.stars_position[0],(sin(self.t_sin - 15) * self.multiplication) + item_frame.left / 1.5))
                surface.blit(self.stars_sheet.subsurface((11 * int(self.target),0),(11,11)),(((cos(self.t_cos - 20) * self.multiplication) + item_frame.left) - self.stars_position[0],(sin(self.t_sin - 20) * self.multiplication) + item_frame.left / 1.5))
                surface.blit(self.stars_sheet.subsurface((11 * int(self.target),0),(11,11)),(((cos(self.t_cos - 13) * self.multiplication) + item_frame.left) - self.stars_position[0],(sin(self.t_sin - 13) * self.multiplication) + item_frame.left / 1.5)) if self.t_cos > 5 else 0
                surface.blit(self.stars_sheet.subsurface((11 * int(self.target),0),(11,11)),(((cos(self.t_cos - 23) * self.multiplication) + item_frame.left) - self.stars_position[0],(sin(self.t_sin - 23) * self.multiplication) + item_frame.left / 1.5)) if self.t_cos > 5 else 0

                # Stars animation
                self.t_cos += (0.1 * dt)
                self.t_sin += (0.1 * dt)
                self.stars_position[0] += (0.85 * dt)

            self.finish = True if self.step[3] else False
