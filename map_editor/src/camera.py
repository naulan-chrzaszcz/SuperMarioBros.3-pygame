import pygame


class Camera(pygame.Rect):
    def __init__(self, x, y, width, height, width_surface, height_surface):
        super().__init__(x, y, width, height)
        self.width_surface = width_surface
        self.height_surface = height_surface

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            match event.key:
                case pygame.K_UP:
                    self.update(self.left, self.top - self.height)
                case pygame.K_DOWN:
                    self.update(self.left, self.top + self.height)
                case pygame.K_RIGHT:
                    self.update(self.left + self.width, self.top)
                case pygame.K_LEFT:
                    self.update(self.left - self.width, self.top)

    def update(self, x, y):
        x = min(x, self.width_surface - self.width)
        y = min(y, self.height_surface - self.height)
        x = max(0, x)
        y = max(0, y)

        super().update(x, y, self.width, self.height)
