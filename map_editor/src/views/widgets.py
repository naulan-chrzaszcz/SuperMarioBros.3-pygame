"""Small reusable Pygame widgets used by launcher and editor views."""

from __future__ import annotations

from typing import Callable, List, Optional, Tuple, Union

import pygame

from ..constants import (
    BORDER_COLOR,
    BUTTON_ACTIVE_COLOR,
    BUTTON_COLOR,
    BUTTON_HOVER_COLOR,
    FIELD_COLOR,
    MUTED_TEXT_COLOR,
    PANEL_COLOR,
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
        """Runs the button action when ``position`` is inside it."""
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


class TextField:
    """A single line text input bound to a model value through callables."""

    def __init__(
        self,
        get_text: Callable[[], str],
        set_text: Callable[[str], None],
        allowed: Callable[[str], bool] = lambda character: character.isprintable(),
        max_length: int = 40,
        placeholder: str = "",
        is_enabled: Callable[[], bool] = lambda: True,
    ) -> None:
        self.get_text = get_text
        self.set_text = set_text
        self.allowed = allowed
        self.max_length = max_length
        self.placeholder = placeholder
        self.is_enabled = is_enabled
        self.focused = False
        self.rect = pygame.Rect(0, 0, 0, 0)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Edits the text with a key or text event. Returns True if it was used."""
        if not self.focused or not self.is_enabled():
            return False
        text = self.get_text()
        if event.type == pygame.TEXTINPUT:
            characters = "".join(c for c in event.text if self.allowed(c))
            self.set_text((text + characters)[: self.max_length])
            return True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
            self.set_text("" if event.mod & pygame.KMOD_CTRL else text[:-1])
            return True
        return False

    def draw(self, surface: pygame.Surface, font: pygame.font.Font, time: float = 0.0) -> None:
        enabled = self.is_enabled()
        focused = self.focused and enabled
        pygame.draw.rect(surface, FIELD_COLOR if enabled else PANEL_COLOR, self.rect, border_radius=4)
        pygame.draw.rect(
            surface, BUTTON_ACTIVE_COLOR if focused else BORDER_COLOR, self.rect, 2 if focused else 1, 4
        )
        text = self.get_text()
        if text:
            image = font.render(text, True, TEXT_COLOR if enabled else MUTED_TEXT_COLOR)
        else:
            image = font.render(self.placeholder, True, MUTED_TEXT_COLOR)
        position = image.get_rect(midleft=(self.rect.x + 8, self.rect.centery))
        surface.set_clip(self.rect.inflate(-4, -4))
        surface.blit(image, position)
        surface.set_clip(None)
        if focused and int(time * 2) % 2 == 0:
            x = position.x + (image.get_width() if text else 0) + 1
            pygame.draw.line(surface, TEXT_COLOR, (x, position.top), (x, position.bottom))


class ListBox:
    """A scrollable list of ``(text, detail)`` items with a single selection."""

    def __init__(
        self,
        items: Callable[[], List[Tuple[str, str]]],
        selected: Callable[[], Optional[int]],
        on_select: Callable[[int], None],
        item_height: int = 28,
    ) -> None:
        self.items = items
        self.selected = selected
        self.on_select = on_select
        self.item_height = item_height
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.scroll = 0

    @property
    def visible_count(self) -> int:
        return max(self.rect.height // self.item_height, 1)

    def item_at(self, position: Tuple[int, int]) -> Optional[int]:
        """Returns the visible item index under ``position``, if any."""
        if not self.rect.collidepoint(position):
            return None
        index = self.scroll + (position[1] - self.rect.y) // self.item_height
        return index if index < len(self.items()) else None

    def click(self, position: Tuple[int, int]) -> Optional[int]:
        """Selects and returns the clicked item index, if any."""
        index = self.item_at(position)
        if index is not None:
            self.on_select(index)
        return index

    def scroll_by(self, delta: int) -> None:
        """Scrolls by item rows while keeping the list within bounds."""
        maximum = max(len(self.items()) - self.visible_count, 0)
        self.scroll = min(max(self.scroll + delta, 0), maximum)

    def ensure_visible(self, index: int) -> None:
        """Scrolls just enough to show ``index``."""
        if index < self.scroll:
            self.scroll = index
        elif index >= self.scroll + self.visible_count:
            self.scroll = index - self.visible_count + 1
        self.scroll_by(0)

    def draw(self, surface: pygame.Surface, font: pygame.font.Font, mouse: Tuple[int, int]) -> None:
        pygame.draw.rect(surface, FIELD_COLOR, self.rect, border_radius=4)
        surface.set_clip(self.rect)
        items = self.items()
        selected = self.selected()
        hovered = self.item_at(mouse)
        for index in range(self.scroll, min(self.scroll + self.visible_count + 1, len(items))):
            rect = pygame.Rect(
                self.rect.x,
                self.rect.y + (index - self.scroll) * self.item_height,
                self.rect.width,
                self.item_height,
            )
            if index == selected:
                pygame.draw.rect(surface, BUTTON_ACTIVE_COLOR, rect)
            elif index == hovered:
                pygame.draw.rect(surface, BUTTON_HOVER_COLOR, rect)
            text, detail = items[index]
            image = font.render(text, True, TEXT_COLOR)
            surface.blit(image, image.get_rect(midleft=(rect.x + 10, rect.centery)))
            if detail:
                color = TEXT_COLOR if index == selected else MUTED_TEXT_COLOR
                image = font.render(detail, True, color)
                surface.blit(image, image.get_rect(midright=(rect.right - 10, rect.centery)))
        surface.set_clip(None)
        pygame.draw.rect(surface, BORDER_COLOR, self.rect, 1, 4)
        if len(items) > self.visible_count:
            self._draw_scrollbar(surface, len(items))

    def _draw_scrollbar(self, surface: pygame.Surface, count: int) -> None:
        height = max(self.rect.height * self.visible_count // count, 12)
        top = self.rect.y + (self.rect.height - height) * self.scroll // max(count - self.visible_count, 1)
        pygame.draw.rect(surface, BORDER_COLOR, (self.rect.right - 6, top, 4, height), border_radius=2)
