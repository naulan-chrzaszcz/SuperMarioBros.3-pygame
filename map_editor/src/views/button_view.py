import pygame

from ..constantes import FONT_SIZE


class ButtonView:
    def __init__(self, model):
        self.model = model
        self.font = pygame.font.SysFont("Arial", FONT_SIZE)

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(
            surface,
            self.model.color,
            pygame.Rect(
                self.model.x, self.model.y, self.model.width, self.model.height
            ),
        )

        text = self.font.render(self.model.text, False, (255, 255, 255))
        surface.blit(
            text,
            pygame.Vector2(
                self.model.x + self.model.width / 2 - text.get_width() / 2,
                self.model.y + self.model.height / 2 - text.get_height() / 2,
            ),
        )
