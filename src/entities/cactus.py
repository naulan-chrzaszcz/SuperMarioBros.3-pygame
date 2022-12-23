from pygame.sprite import (Sprite)


class Cactus(Sprite):

    def __init__(self, class_access, sheet, position):
        Sprite.__init__(self, class_access.all_sprites)

        self.id = 'cactus'
        self.frame = .0
        self.dt = .0

        self.sheet = sheet
        self.animation()

        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]

    def animation(self):
        self.image = self.sheet.subsurface((int(self.frame)%4 * 16, 2 * 16), (16, 16))
        self.frame += (.05 * self.dt)

    def update(self, dt):
        self.dt = dt
        self.animation()
