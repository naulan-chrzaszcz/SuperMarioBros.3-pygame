from pygame.transform import (flip)
from pygame.sprite import (Sprite)
from pygame.locals import *
from math import (sin)
import json


class Player(Sprite):

    def __init__(self, all_sprites, sheet, position):
        Sprite.__init__(self, all_sprites)

        self.keys = None
        self.directory = 'res/'
        self.open_save()

        # ### BOOLEAN VARIABLES ###
        self.move = {'right': False, 'left': False, 'up': False, 'down': False, 'jump': False, 'afk': True,
                     'run': False}
        self.collide = {'top': False, 'bottom': False, 'right': False, 'left': False}
        self.look = {'right': True, 'left': False}
        self.get_y = False
        self.air = True

        # ### STRING VARIABLES ###
        self.inventory = self.data_save['PowerUpInventory']
        self.state = self.data_save['State']
        self.who = self.data_save['Who']
        self.where = 'Stage_Menu'
        self.id = 'player'

        # ### INT/FLOAT VARIABLES ###
        self.score = self.data_save['Score']
        self.coins = self.data_save['Coins']
        self.life = self.data_save['Life']
        self.verify_move = 0
        self.kill_frag = 0
        self.health = 1
        self.frame = 0
        self.velocity = 4.2
        self.t_air = .0
        self.dt = .0
        self.t = .0

        self.player_sheet = sheet[0]
        if self.where == 'World':
            self.points_sheet = sheet[1]
        self.animation()

        # ### RECT VARIABLES ###
        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]
        # For jump() function
        self.y_init = self.rect.bottom - 17
        self.x_init = self.rect.x

    def open_save(self, mode='Read'):
        with open(rf'{self.directory}save.json') as save:
            self.data_save = json.load(save) if mode == 'Read' else None
        if mode == 'Write':
            TMP_DATA = {"PowerUpInventory": self.inventory, "Position": [self.rect.x, self.rect.y], "Score": self.score,
                        "State": self.state, "Coins": self.coins, "Life": self.life, "Who": self.who}
            with open(rf'{self.directory}save.json', 'w') as save:
                json.dump(TMP_DATA, save, indent=4)

    def orientation(self, lgn, frame, sprite_size=(16, 16)):
        self.image = flip(self.player_sheet.subsurface((frame * 16, lgn * 16), sprite_size), True, False) if self.look[
            'right'] else self.player_sheet.subsurface((frame * 16, lgn * 16), sprite_size)

    def points_system(self):
        self.kill_frag += 1
        if self.kill_frag < 9:
            self.score += (50 * (self.kill_frag * 2))
        elif self.kill_frag >= 9:
            # self.sfx[5].play(loops=0)
            self.life += 1

    def draw_points(self, surface, position):
        surface.blit(self.points_sheet.subsurface((self.kill_frag + 1) if self.kill_frag < 9 else 9, 0, 10,
                                                  11 if self.kill_frag < 4 else 15 if self.kill_frag >= 4 else 0),
                     self.camera.apply(self, position[0], position[1])) if self.kill_frag != 9 else None
        surface.blit(self.points_sheet.subsurface(0, 0, 8, 16),
                     self.camera.apply(self, position[0], position[1])) if self.kill_frag == 9 else None

    def animation(self):
        if self.where == 'Stage_Menu':
            self.frame += (.05 * self.dt)
            self.image = self.player_sheet.subsurface(48, 32 + int(self.frame % 2) * 16, 16, 16)
        else:
            if all([self.move['afk'], self.state != 'dead']):
                return self.orientation(0, 0)
            if self.state == 'dead':
                return self.orientation(1, 3)
            # Start default animation if not dead
            if all([self.state != 'dead', self.move['afk'] == 0, self.move['jump'] == 0, self.air == 0,
                    any([self.move['right'], self.move['left']])]):
                if self.state != 'big':
                    self.frame += (.25 * self.dt)
                    self.orientation(0, int(self.frame % 2))
                else:
                    self.rect = self.image.get_rect()
                    return self.orientation(0, int(self.frame % 2))

    def events(self):
        if self.where == 'Stage_Menu':
            if abs(self.verify_move) != 16:
                if any([self.move['up'], self.move['down'], self.move['left'], self.move['right']]):
                    self.verify_move += int(4.2 * self.dt)

                # Keyboard event
                self.move['up'], self.move['down'], self.move['right'], self.move['left'] = self.keys[f'{K_z}'], \
                self.keys[
                    f'{K_s}'], self.keys[f'{K_d}'], self.keys[f'{K_q}']
                # Joystick event

            if abs(self.verify_move) >= 16:
                self.move['up'], self.move['down'], self.move['right'], self.move['left'] = False, False, False, False
                if all(
                        [any([self.move['up'] == 0, self.move['down'] == 0, self.move['right'] == 0,
                              self.move['left'] == 0]),
                         any([self.keys[f'{K_z}'], self.keys[f'{K_s}'], self.keys[f'{K_d}'],
                              self.keys[f'{K_q}']])]) is False:
                    self.verify_move = 0
        else:
            if self.collide['right'] is False:
                self.move['right'] = self.keys[f'{K_d}']
            if self.collide['left'] is False:
                self.move['left'] = self.keys[f'{K_q}']
            if self.move['right'] is False and self.move['left'] is False:
                self.x_init = self.rect.x
                self.t_speed = 0
            if self.air == 0 and self.move['jump'] is False:
                self.x_init = self.rect.x
                self.y_init = self.rect.bottom - 17
                # self.sfx[choice((1, 2))].play(loops=0)
                self.t = 0
            if self.keys[f'{K_SPACE}']:
                self.move['jump'] = True
            if self.keys[f'{K_SPACE}'] is False:
                self.move['jump'] = False
            self.move['afk'] = False if any(
                [self.keys[f'{K_d}'], self.keys[f'{K_q}'], self.keys[f'{K_SPACE}']]) else True

    def jump(self):
        self.orientation(1, .01)
        # self.rect.y = -(1/2) * -gravity * real_time² + (speed_init * sin( alpha° ) * real_time + y_init
        self.rect.y = (-(1 / 2) * -9.81 * self.t ** 2 + ((self.velocity * 10) * sin(5)) * self.t) + self.y_init
        self.t += (.2 * self.dt)

    def move_right(self):
        self.look['right'] = True
        self.look['left'] = False
        if self.where == 'Stage_Menu':
            self.rect.left += int(4.2 * self.dt)
        else:
            self.rect.left += (self.velocity * self.dt)

    def move_left(self):
        self.look['right'] = False
        self.look['left'] = True
        if self.where == 'Stage_Menu':
            self.rect.left -= int(4.2 * self.dt)
        else:
            self.rect.left -= (self.velocity * self.dt)

    def move_up(self):
        self.rect.top -= int(4.2 * self.dt)

    def move_down(self):
        self.rect.top += int(4.2 * self.dt)

    def collide_test(self, sprite):
        collision_tolerance = 10
        if self.rect.colliderect(sprite.rect):
            # ### TOP COLLISION ### -----------------------------------------
            if abs(self.rect.top - sprite.rect.bottom) < collision_tolerance:
                if sprite.id != 'platforms' and sprite.id != 'coin':
                    self.collide['top'], self.air = True, True
                    self.collide['bottom'], self.collide['left'], self.collide['right'], self.move[
                        'jump'] = False, False, False, False
                    self.rect.top = sprite.rect.bottom
                if sprite.id == 'lootblock':
                    sprite.state = 'activated'
                if sprite.id == 'coin' and sprite.step == 0:
                    sprite.state = 'pickup'
                    self.coins += 1
                if sprite.id == 'vegetable' and sprite.start is False:
                    sprite.start = True
                if sprite.id == 'cactus' and self.where == 'Stage_Menu':
                    self.rect.top = sprite.rect.bottom

            # ### BOTTOM COLLISION ### ----------------------------------------
            elif abs(self.rect.bottom - sprite.rect.top) < collision_tolerance:
                if sprite.id == 'platforms':
                    if any([sprite.offset_img[0] == 0, sprite.offset_img[0] == 1, sprite.offset_img[0] == 2]) and \
                            self.move['jump'] is False:
                        self.collide['top'], self.collide['left'], self.collide[
                            'right'], self.air, self.get_y = False, False, False, False, False
                        self.collide['bottom'] = True
                        self.rect.bottom = sprite.rect.top + 1
                        self.y_init = sprite.rect.top - 18
                        self.kill_frag, self.t, self.t_air = 0, 0, 0
                if all([sprite.id != 'vegetable', sprite.id != 'platforms', sprite.id != 'coin', sprite.id != 'cloud']):
                    self.collide['top'], self.collide['left'], self.collide[
                        'right'], self.air, self.get_y = False, False, False, False, False
                    self.collide['bottom'] = True
                    self.rect.bottom = sprite.rect.top + 1
                    self.y_init = sprite.rect.top - 18
                    self.kill_frag, self.t, self.t_air = 0, 0, 0

                if sprite.id == 'coin' and sprite.step == 0:
                    sprite.state = 'pickup'
                    self.coins += 1
                if sprite.id == 'vegetable' and sprite.start == 0:
                    sprite.start = True
                if any([sprite.id == 'goomba', sprite.id == 'koopa']) and sprite.step == 0:
                    sprite.state = 'dead'
                    self.points_system()

            # ### RIGHT COLLISION ### -----------------------------------------
            elif abs(self.rect.right - sprite.rect.left) < collision_tolerance:
                if all([sprite.id != 'vegetable', sprite.id != 'cloud', sprite.id != 'platforms', sprite.id != 'coin']):
                    self.collide['top'], self.collide['left'], self.collide['bottom'] = False, False, False
                    self.collide['right'] = True
                    self.rect.right = sprite.rect.left

                if sprite.id == 'coin':
                    self.coins += 1
                    sprite.kill()
                if sprite.id == 'vegetable' and sprite.start == 0:
                    sprite.start = True
                if any([sprite.id == 'goomba', sprite.id == 'koopa']):
                    self.state = 'dead'

            # ### LEFT COLLISION ### ------------------------------------------
            elif abs(self.rect.left - sprite.rect.right) < collision_tolerance:
                if all([sprite.id != 'vegetable', sprite.id != 'platforms', sprite.id != 'coin', sprite.id != 'cloud']):
                    self.collide['top'], self.collide['bottom'], self.collide['right'] = False, False, False
                    self.collide['left'] = True
                    self.rect.left = sprite.rect.right

                if any([sprite.id == 'goomba', sprite.id == 'koopa']):
                    self.state = 'dead'
                if sprite.id == 'coin' and sprite.step == 0:
                    sprite.state = 'pickup'
                    self.coins += 1
                if sprite.id == 'vegetable' and sprite.start == 0:
                    sprite.start = True

            else:
                self.collide['top'], self.collide['bottom'], self.collide['right'], self.collide[
                    'left'] = False, False, False, False
                if self.move['jump'] is False:
                    self.air = True
                    if self.get_y == 0:
                        self.y_init = self.rect.y
                        self.get_y = True

    def update(self, dt):
        self.dt = dt

        if self.coins == 100:
            self.life += 1
            self.coins = 0
        if self.air and self.where != 'Stage_Menu':
            self.rect.y = (-(1 / 2) * -9.81 * self.t_air ** 2 + (
                        (self.velocity * 10) * sin(90)) * self.t_air) + self.y_init
            self.t_air += (.045 * dt)

        self.events()
        self.move_right() if self.move['right'] else None
        self.move_left() if self.move['left'] else None
        self.move_up() if self.move['up'] else None
        self.move_down() if self.move['down'] else None
        self.jump() if self.move['jump'] else None
        self.animation()
