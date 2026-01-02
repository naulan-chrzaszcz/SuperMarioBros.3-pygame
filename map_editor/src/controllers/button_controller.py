import pygame


class ButtonController:
    def __init__(self, model) -> None:
        self.model = model

    def handle_event(self, event: pygame.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = pygame.mouse.get_pos()
            if (
                self.model.x <= x <= self.model.x + self.model.width
                and self.model.y <= y <= self.model.y + self.model.height
            ):
                self.model.on_click()
