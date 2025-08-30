from typing import Tuple

import pygame

from .constantes import FONT_SIZE


class Button(pygame.Rect):
    """A simple clickable button."""

    def __init__(
        self, x: int, y: int, width: int, height: int, color: Tuple[int, int, int]
    ) -> None:
        """Create a new Button.

        Args:
            x (int): X-axis position of the button
            y (int): Y-axis position of the button
            width (int): Width of the button
            height (int): Height of the button
            color (Tuple[int, int, int]): RGB color of the button
        """
        super().__init__(x, y, width, height)
        self.color = color

        self.font = pygame.font.SysFont("Arial", FONT_SIZE)
        self.value = None
        """Value associated with the button."""
        self._text = None
        self._text_pos = None
        self.on_click = None
        """Function to call when clicked."""

    @property
    def text(self) -> pygame.Surface:
        """Get the button's text surface.

        Returns:
            pygame.Surface: Surface containing the button's text. 
            If no text is set, returns an empty surface.
        """
        if not self._text:
            return pygame.Surface((0, 0))
        return self._text

    @text.setter
    def text(self, text: str) -> None:
        """Set the text to be displayed on the button.

        Args:
            text (str): The new text for the button.
        """
        self._text = None
        self._text_pos = None
        if text and isinstance(text, str):
            self._text = self.font.render(text, False, (255, 255, 255))
            self._text_pos = pygame.Vector2(
                self.x + self.width / 2 - self._text.get_width() / 2,
                self.y + self.height / 2 - self._text.get_height() / 2,
            )

    def handle_event(self, event: pygame.Event) -> None:
        """Handle the button click event.

        Args:
            event (pygame.Event): The event to handle.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.collidepoint(pygame.mouse.get_pos()):
                if self.on_click:
                    self.on_click()

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the button on the given surface.

        Args:
            surface (pygame.Surface): The surface to draw the button on.
        """
        pygame.draw.rect(surface, self.color, self)
        surface.blit(self.text, self._text_pos)
