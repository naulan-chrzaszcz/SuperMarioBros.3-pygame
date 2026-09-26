from __future__ import annotations

from typing import List, Optional

import pygame

from ..constants import BLACK, WHITE
from ..inputs.config import Action
from ..levels import LevelInfo
from .scene import GameContext, Scene

MUTED = (140, 140, 140)


class CustomLevelsScene(Scene):
    """Lists the maps of ``res/maps`` (made with the map editor) to play them."""

    VISIBLE_ROWS = 11
    ROW_HEIGHT = 14
    LIST_TOP = 44

    def __init__(self, context: GameContext):
        super().__init__(context)
        self.levels: List[LevelInfo] = []
        self.selected = 0
        self.scroll = 0
        self.message: Optional[str] = None

    @property
    def items(self) -> int:
        """The levels, then "open the map editor"."""
        return len(self.levels) + 1

    @property
    def editor_selected(self) -> bool:
        return self.selected == len(self.levels)

    def on_enter(self) -> None:
        super().on_enter()
        self.levels = self.context.levels.refresh()
        self.selected = min(self.selected, self.items - 1)
        self.message = None
        self._scroll_to_selection()

    def on_action(self, action: Action) -> None:
        if action == Action.UP:
            self.select(self.selected - 1)
        elif action == Action.DOWN:
            self.select(self.selected + 1)
        elif action == Action.CONFIRM:
            self.confirm()
        elif action == Action.BACK:
            self.manager.change_scene("main_menu")

    def select(self, index: int) -> None:
        self.selected = index % self.items
        self.message = None
        self._scroll_to_selection()

    def confirm(self) -> None:
        if self.editor_selected:
            self.context.open_editor()
            return
        level = self.levels[self.selected]
        if not level.playable:
            self.message = level.error
            return
        self.context.play_level(level, lambda cleared: self.manager.change_scene("custom_levels"))

    def _scroll_to_selection(self) -> None:
        if self.selected < self.scroll:
            self.scroll = self.selected
        elif self.selected >= self.scroll + self.VISIBLE_ROWS:
            self.scroll = self.selected - self.VISIBLE_ROWS + 1

    def draw(self) -> None:
        surface = self.surface
        font = self.context.font
        width, height = surface.get_size()
        surface.fill(BLACK)
        pygame.draw.rect(surface, WHITE, surface.get_rect().inflate(-16, -16), 1)

        title = font.render("CUSTOM LEVELS")
        surface.blit(title, (width // 2 - title.get_width() // 2, 20))

        left = 48
        for index in range(self.scroll, min(self.items, self.scroll + self.VISIBLE_ROWS)):
            y = self.LIST_TOP + (index - self.scroll) * self.ROW_HEIGHT
            if index == len(self.levels):
                text, detail = "OPEN THE MAP EDITOR", ""
            else:
                level = self.levels[index]
                text = (level.title or level.name).replace("_", " ")
                detail = f"{level.size[0]}X{level.size[1]}" if level.size else ""
                if not level.playable:
                    detail = "ERROR"
            image = font.render(text)
            surface.blit(image, (left, y))
            if detail:
                detail_image = font.render(detail)
                surface.blit(detail_image, (width - left - detail_image.get_width(), y))
            if index == self.selected:
                pygame.draw.polygon(surface, WHITE, [(left - 14, y), (left - 14, y + 7), (left - 7, y + 3)])

        if self.scroll > 0:
            pygame.draw.polygon(surface, MUTED, [(width // 2 - 4, 38), (width // 2 + 4, 38), (width // 2, 34)])
        if self.scroll + self.VISIBLE_ROWS < self.items:
            bottom = self.LIST_TOP + self.VISIBLE_ROWS * self.ROW_HEIGHT
            pygame.draw.polygon(
                surface, MUTED, [(width // 2 - 4, bottom), (width // 2 + 4, bottom), (width // 2, bottom + 4)]
            )

        if not self.levels:
            hint = font.render("NO LEVEL IN RES MAPS")
            surface.blit(hint, (width // 2 - hint.get_width() // 2, self.LIST_TOP + 30))

        footer = self.message or "A PLAY     ESC BACK"
        lines = self.context.font.wrap(footer, 52)
        for index, line in enumerate(lines[-2:]):
            image = font.render(line)
            surface.blit(image, (width // 2 - image.get_width() // 2, height - 40 + index * 11))
