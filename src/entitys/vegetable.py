from pygame.sprite import Sprite


class Vegetable(Sprite):

    def __init__(self, group_sprite, sheet, position):
        Sprite.__init__(self, group_sprite)

        self.id = 'vegetable'
        self.start = False

        self.frame = 0
        self.dt = .0

        self.sheet = sheet
        self.image = sheet.subsurface((80, 0), (16, 16))

        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]

    def animation(self):
        if self.start:
            if int(self.frame) > 2:
                self.image = self.sheet.subsurface((80, 0), (16, 16))
                self.frame = 0
                self.start = False
            self.image = self.sheet.subsurface((80, int(self.frame) * 16), (16, 16))
            self.frame += (.1 * self.dt)

    def update(self, dt):
        self.dt = dt
        self.animation()
