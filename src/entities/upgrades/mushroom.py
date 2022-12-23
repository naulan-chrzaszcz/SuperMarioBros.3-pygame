from pygame.sprite import (Sprite)


class Mushroom(Sprite):

    def __init__(self, group, sheet, position, color):
        Sprite.__init__(self, group)

        self.id = 'mushroom'
        self.color = color
        self.image = sheet

        self.move = {'right': 1, 'left': 0}

        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]

        self.dt = 0

    def move_right(self):   self.rect.x += (2.5 * self.dt)

    def move_left(self):    self.rect.x -= (2.5 * self.dt)

    def update(self, dt):
        self.dt = dt

        self.move_right() if self.move['right'] else 0
        self.move_left() if self.move['left'] else 0
