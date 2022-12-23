from pygame.sprite import (Sprite, spritecollide)
from pygame.transform import (flip)
from random import (choice)


class Koopa(Sprite):

    def __init__(self, class_access, sheet, position):
        self.groups = class_access.all_sprites
        # Init pygame.sprite.Sprite and add Groups for this class
        Sprite.__init__(self, self.groups)

        self.sheet = sheet

        # ### STRING VALUES ###
        self.state = 'normal'
        self.id = 'koopa'

        # ### DICT VALUES ###
        self.last_orientation = {'look_right': False, 'look_left': True}
        self.move = {'right': choice((False, True, False)), 'left': True}
        self.move['left'] = True if self.move['right'] is False else False

        # ### BOOLEAN VARIABLES ###
        self.air = False

        # ### INT/FLOAT VALUES ###
        self.velocity = 1
        self.damage = 1
        self.frame = 0
        self.step = 0
        self.dt = 0

        # ### RECT VALUES ###
        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1] - 10

    def orientation(self, frame=0):
        self.image = flip(self.koopa_img[self.state][int(frame)], True, False) if self.last_orientation[
            'look_right'] else self.koopa_img[self.state][int(frame)]

    def animation(self):
        self.orientation(self.frame % 2) if self.state == 'normal' else 0
        self.frame += (0.15 * self.dt)

    def move_right(self):
        self.last_orientation['look_right'] = True
        self.last_orientation['look_left'] = False
        self.rect = self.rect.move(self.velocity, 0)

    def move_left(self):
        self.last_orientation['look_right'] = False
        self.last_orientation['look_left'] = True
        self.rect = self.rect.move(-self.velocity, 0)

    def collide_test(self):
        # In spritecollide(*arg, **arg, boolean) boolean value allow to kill the sprite
        target_hit_list = spritecollide(self, self.groups, False)
        if target_hit_list == []:
            self.air = True

        collision_tolerance = 4
        for target in target_hit_list:
            if self.rect.colliderect(target.rect):
                # Top collision
                if abs(self.rect.top - target.rect.bottom) < collision_tolerance:
                    pass
                # Bottom collision
                elif abs(self.rect.bottom - target.rect.top) < collision_tolerance:
                    self.rect.bottom = target.rect.top + 2
                # Right collision
                elif abs(self.rect.right - target.rect.left) < collision_tolerance:
                    if all([target.id != 'vegetable', target.id != 'platforms', target.id != 'player']):
                        self.rect.right = target.rect.left
                        self.move['right'] = False
                        self.move['left'] = True
                # left collision
                elif abs(self.rect.left - target.rect.right) < collision_tolerance:
                    if all([target.id != 'vegetable', target.id != 'platforms', target.id != 'player']):
                        self.rect.left = target.rect.right
                        # Continue to move right
                        self.move['left'] = False
                        self.move['right'] = True

    def update(self, dt):
        self.dt = dt

        self.move_right() if self.move['right'] else None
        self.move_left() if self.move['left'] else None
        if self.air: self.rect.y += 4
        self.collide_test()
        self.animation()
