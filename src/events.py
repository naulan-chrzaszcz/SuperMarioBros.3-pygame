import json
import sys

from pygame import event, joystick, quit, draw
from collections import Counter
from pygame.locals import *
from src.font import Font


class Events(object):

    def __init__(self, img):
        self.font = Font()
        # Add joysticks and init joystick
        self.joysticks = []
        for i in range(joystick.get_count()):
            self.joysticks.append(joystick.Joystick(i))
        for controller in self.joysticks:
            controller.init()

        with open(r'res/save.json') as save_file:
            tmp = json.load(save_file)
        self.controller_name = None

        self.is_calibrate = tmp['ControllerCalibrate']
        self.finish_calibrate = False
        self.enable_keyboard = True
        self.enable_joystick = False

        self.keys_pressed = {f'{K_a}': False, f'{K_z}': False, f'{K_e}': False, f'{K_r}': False, f'{K_t}': False,
                             f'{K_y}': False, f'{K_u}': False, f'{K_i}': False, f'{K_o}': False, f'{K_p}': False,
                             f'{K_q}': False, f'{K_s}': False, f'{K_d}': False, f'{K_f}': False, f'{K_g}': False,
                             f'{K_h}': False, f'{K_j}': False, f'{K_k}': False, f'{K_l}': False, f'{K_m}': False,
                             f'{K_w}': False, f'{K_x}': False, f'{K_c}': False, f'{K_v}': False, f'{K_b}': False,
                             f'{K_n}': False, f'{K_SPACE}': False}
        self.joys_pressed = {'Y': None, 'B': None, 'A': None, 'X': None, 'UP': None, 'DOWN': None, 'RIGHT': None,
                             'LEFT': None, 'AXIS_UP': None, 'AXIS_DOWN': None, 'AXIS_RIGHT': None, 'AXIS_LEFT': None,
                             'HAT_H': None, 'HAT_V': None, 'RB': None, 'RT': None, 'LB': None, 'LT': None,
                             'START': None, 'SELECT': None}
        self.axis_get_list = []
        self.get()

        self.button_img = img["buttonSheet"]
        self.controller_img = img["controller"]
        self.background = img["introBG"]

        self.axis_value = 0

    def calibrate(self, surface):
        surface.fill((0, 0, 0))

        current_button = None
        current_axis = None
        for pressed in event.get():
            if pressed.type == QUIT:
                quit(), sys.exit()

            if pressed.type == JOYBUTTONDOWN:
                current_button = pressed.button
            if pressed.type == JOYAXISMOTION:
                if pressed.value >= .90 or -.90:
                    current_axis = pressed.axis
                self.axis_value = pressed.value

        # ### IMG ### =------------------------------------------------------
        self.background.set_alpha(255)
        surface.blit(self.background, (0, 0))
        surface.blit(self.controller_img, (surface.get_width()/3, surface.get_height()/4))
        A_img = self.button_img.copy()
        A_img = A_img.subsurface(0, 16, 10, 10)
        A_img.set_alpha(125 if self.joys_pressed['A'] is None else 255)
        surface.blit(A_img, (261, (surface.get_height()/4) + 34))
        B_img = self.button_img.copy()
        B_img = B_img.subsurface(10, 16, 10, 10)
        B_img.set_alpha(125 if self.joys_pressed['B'] is None else 255)
        surface.blit(B_img, (271, (surface.get_height()/4) + 24))
        X_img = self.button_img.copy()
        X_img = X_img.subsurface(20, 16, 10, 10)
        X_img.set_alpha(125 if self.joys_pressed['X'] is None else 255)
        surface.blit(X_img, (251, (surface.get_height()/4) + 24))
        Y_img = self.button_img.copy()
        Y_img = Y_img.subsurface(30, 16, 10, 10)
        Y_img.set_alpha(125 if self.joys_pressed['Y'] is None else 255)
        surface.blit(Y_img, (261, (surface.get_height()/4) + 14))

        draw.circle(surface, (255, 255, 255), (
            186 + (self.joys_pressed['AXIS_RIGHT'][1] if self.joys_pressed['AXIS_RIGHT'] is not None else 0) or (
                self.joys_pressed['AXIS_LEFT'][1] if self.joys_pressed['AXIS_LEFT'] is not None else 0)*5,
            86 + (self.joys_pressed['AXIS_UP'][1] if self.joys_pressed['AXIS_UP'] is not None else 0) or (
                self.joys_pressed['AXIS_DOWN'][1] if self.joys_pressed['AXIS_DOWN'] is not None else 0)*5), 8)
        draw.circle(surface, (255, 255, 255), (245, 116), 8)

        self.font.draw_msg(surface, [surface.get_width()/1.95, surface.get_height()/1.6], 'PRESS') if any(
            [self.joys_pressed['A'] is None, self.joys_pressed['B'] is None, self.joys_pressed['X'] is None,
             self.joys_pressed['Y'] is None, ]) else 0
        if self.joys_pressed['A'] is None:
            surface.blit(self.button_img.subsurface(0, 0, 16, 16),
                         (surface.get_width()/2.10, (surface.get_height()/1.6) + 10))
            if current_button is not None:
                self.joys_pressed['A'] = [current_button, False]
                event.clear()

        elif self.joys_pressed['B'] is None:
            surface.blit(self.button_img.subsurface(16, 0, 16, 16),
                         (surface.get_width()/2.10, (surface.get_height()/1.6) + 10))
            if current_button is not None:
                self.joys_pressed['B'] = [current_button, False]
                event.clear()

        elif self.joys_pressed['X'] is None:
            surface.blit(self.button_img.subsurface(32, 0, 16, 16),
                         (surface.get_width()/2.10, (surface.get_height()/1.6) + 10))
            if current_button is not None:
                self.joys_pressed['X'] = [current_button, False]
                event.clear()

        elif self.joys_pressed['Y'] is None:
            surface.blit(self.button_img.subsurface(48, 0, 16, 16),
                         (surface.get_width()/2.10, (surface.get_height()/1.6) + 10))
            if current_button is not None:
                self.joys_pressed['Y'] = [current_button, False]
                event.clear()

        elif self.joys_pressed['AXIS_RIGHT'] is None:
            if current_axis is not None:
                self.axis_get_list.append([current_axis, self.axis_value])
                if len(self.axis_get_list) == 5:
                    axis_, count_ = Counter([self.axis_get_list[n][0] for n in range(5)]).most_common()
                    print(axis_, count_)
                    axis, count = max(Counter([self.axis_get_list[n][0] for n in range(5)]).most_common())
                    print(axis, count)
                    axis_value_abs = max([self.axis_get_list[n][1] for n in range(5)])
                    self.joys_pressed['AXIS_RIGHT'] = [axis, -self.axis_value]
                    event.wait(2)
                    event.clear()

        elif self.joys_pressed['AXIS_LEFT'] is None:
            if current_axis is not None:
                if abs(self.axis_value) <= .80:
                    self.joys_pressed['AXIS_LEFT'] = [current_axis, self.axis_value]
                    event.wait(2)
                    event.clear()

        elif self.joys_pressed['AXIS_UP'] is None:
            if current_axis is not None:
                if abs(self.axis_value) <= .80:
                    self.joys_pressed['AXIS_UP'] = [current_axis, -self.axis_value]
                    event.wait(2)
                    event.clear()

        elif self.joys_pressed['AXIS_DOWN'] is None:
            if current_axis is not None:
                if abs(self.axis_value) <= .80:
                    self.joys_pressed['AXIS_DOWN'] = [current_axis, self.axis_value]
                    event.wait(2)
                    event.clear()

    def get(self):
        for pressed in event.get():
            if pressed.type == QUIT:
                quit(), sys.exit()

            if pressed.type == JOYDEVICEADDED:
                self.enable_keyboard = False
                self.enable_joystick = True
                self.joysticks = [joystick.Joystick(i) for i in range(joystick.get_count())]
                for joys in self.joysticks:
                    self.controller_name = joys.get_name()

            if pressed.type == JOYDEVICEREMOVED:
                self.enable_keyboard = True
                self.enable_joystick = False
                self.joysticks = [joystick.Joystick(i) for i in range(joystick.get_count())]

            if self.enable_keyboard:
                if pressed.type == KEYDOWN:
                    if pressed.key == K_ESCAPE:
                        quit(), sys.exit()
                    self.keys_pressed[f'{pressed.key}'] = True

                if pressed.type == KEYUP:
                    self.keys_pressed[f'{pressed.key}'] = False

            if self.enable_joystick and self.is_calibrate:
                if pressed.type == JOYBUTTONDOWN:
                    if str(pressed.button) == self.joys_pressed['Y'][0]:
                        self.joys_pressed['Y'][1] = True
                if pressed.type == JOYBUTTONUP:
                    pass

                if pressed.type == JOYAXISMOTION:
                    if pressed.axis == 0:
                        self.joys_pressed['AXIS_H'] = pressed.value
                    if pressed.axis == 1:
                        self.joys_pressed['AXIS_V'] = pressed.value

                if pressed.type == JOYHATMOTION:
                    print(event)
