from pygame.sprite import (Sprite, spritecollide)
from pygame.transform import (flip)
from random import (choice)


class Goomba(Sprite):

    def __init__(self, class_access, sheet, position):
        self.groups = class_access.all_sprites
        Sprite.__init__(self, self.groups)

        self.sheet = sheet

        # ### STRING VARIABLES ###
        self.state = 'normal'
        self.id = 'goomba'

        # ### DICT VARIABLES ###
        self.move = {'right': choice((0, 1)), 'left': 1}
        if self.move['right'] == 0:
            self.move['left'] = 1
        else:
            self.move['left'] = 0
        self.air = 0

        # ### INT/FLOAT VARIABLES ###
        self.velocity = 1
        self.damage = 1
        self.frame = 0
        self.step = 0

        # ### RECT VALUES ###
        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]

    def animation(self):

        # Is dead
        if self.state == 'dead':
            if self.step == 0:
                # self.sfx[0].play(loops=0)
                self.move['right'] = 0
                self.move['left'] = 0
                self.step += 1
            elif self.step <= 10:
                self.image = self.goomba_img[self.state][0]
            else:
                # Delete the current sprite
                self.remove(self.groups)
            self.step += 1
            return self.image
        # Not dead
        else:
            if self.frame >= 35:
                self.image = flip(self.goomba_img[self.state][0], 1, 0)
            elif self.frame <= 50:
                self.image = flip(self.goomba_img[self.state][0], 0, 0)
            if self.frame == 65:
                self.frame = 0
            self.frame += 5
            return self.image

    def move_right(self):
        self.rect = self.rect.move(self.velocity, 0)

    def move_left(self):
        self.rect = self.rect.move(-self.velocity, 0)

    def collide_test(self):
        target_hit_list = spritecollide(self, self.groups, 0)
        if target_hit_list == []:
            self.air = 1

        collision_tolerance = 4
        for target in target_hit_list:
            if self.rect.colliderect(target.rect):
                # ### TOP COLLISION ###
                if abs(self.rect.top - target.rect.bottom) < collision_tolerance:
                    pass
                # ### BOTTOM COLLISION ###
                elif abs(self.rect.bottom - target.rect.top) < collision_tolerance:
                    self.rect.bottom = target.rect.top
                # ### RIGHT COLLISION ###
                elif abs(self.rect.right - target.rect.left) < collision_tolerance:
                    if all([target.id != 'vegetable', target.id != 'platforms', target.id != 'player']):
                        self.rect.right = target.rect.left
                        self.move['right'] = 0
                        self.move['left'] = 1
                # ### LEFT COLLISION ###
                elif abs(self.rect.left - target.rect.right) < collision_tolerance:
                    if all([target.id != 'vegetable', target.id != 'platforms', target.id != 'player']):
                        self.rect.left = target.rect.right
                        self.move['left'] = 0
                        self.move['right'] = 1

    def update(self, dt):
        self.move_right() if self.move['right'] else 0
        self.move_left() if self.move['left'] else 0
        if self.air: self.rect.y += 4
        self.collide_test()
        self.animation()
