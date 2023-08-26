from pygame import Rect


class Camera(object):
    def __init__(self, size):
        # ### INT/FLOAT VARIABLES ###
        self.width = size[0]
        self.height = size[1]

        # ### RECT VARIABLES ###
        self.rect = Rect(0, 0, size[0], size[1])

        self.apply_rect = lambda rect: rect.move(self.rect.topleft)

    def apply(self, entity, add_x=0, add_y=0):
        return entity.rect.move((self.rect.topleft[0] + add_x), (self.rect.topleft[1] + add_y))

    def update(self, target):
        x = -target.rect.x + 100
        y = -target.rect.y

        # limit scrolling to map size
        x = min(0, x)  # left
        y = min(0, y)  # top
        x = max(-self.width, x)  # right
        y = max(-(self.height - 237), y)  # bottom
        self.rect.update(x, y, self.width, self.height)
