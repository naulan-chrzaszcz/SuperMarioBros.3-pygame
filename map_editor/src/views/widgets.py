from typing import Callable, Optional, Tuple, Union

import pygame

from ..constantes import (
    BUTTON_ACTIVE_COLOR,
    BUTTON_COLOR,
    BUTTON_HOVER_COLOR,
    MUTED_TEXT_COLOR,
    TEXT_COLOR,
)


class Button:
    """A clickable button. Without ``on_click`` it is drawn as a plain label.

    ``label``, ``is_active`` and ``is_enabled`` may be callables so that the
    button always reflects the current editor state.
    """

    def __init__(
        self,
        label: Union[str, Callable[[], str]],
        on_click: Optional[Callable[[], None]] = None,
        is_active: Callable[[], bool] = lambda: False,
        is_enabled: Callable[[], bool] = lambda: True,
    ) -> None:
        self.label = label
        self.on_click = on_click
        self.is_active = is_active
        self.is_enabled = is_enabled
        self.rect = pygame.Rect(0, 0, 0, 0)

    @property
    def text(self) -> str:
        return self.label() if callable(self.label) else self.label

    def click(self, position: Tuple[int, int]) -> bool:
        if self.on_click is None or not self.rect.collidepoint(position):
            return False
        if self.is_enabled():
            self.on_click()
        return True

    def draw(
        self, surface: pygame.Surface, font: pygame.font.Font, mouse: Tuple[int, int]
    ) -> None:
        enabled = self.is_enabled()
        if self.on_click is not None:
            if self.is_active():
                color = BUTTON_ACTIVE_COLOR
            elif enabled and self.rect.collidepoint(mouse):
                color = BUTTON_HOVER_COLOR
            else:
                color = BUTTON_COLOR
            pygame.draw.rect(surface, color, self.rect, border_radius=4)

        text = font.render(self.text, True, TEXT_COLOR if enabled else MUTED_TEXT_COLOR)
        surface.blit(text, text.get_rect(center=self.rect.center))
