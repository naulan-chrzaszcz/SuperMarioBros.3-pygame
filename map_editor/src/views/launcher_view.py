from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import pygame

from ..constantes import (
    BACKGROUND_COLOR,
    BORDER_COLOR,
    BUTTON_HEIGHT,
    DEFAULT_MAP_SIZE,
    ERROR_COLOR,
    FONT_SIZE,
    INFO_COLOR,
    MUTED_TEXT_COLOR,
    PANEL_COLOR,
    SUCCESS_COLOR,
    TEXT_COLOR,
    WARNING_COLOR,
)
from ..models import MessageLevel, Tileset
from ..models.launcher_model import LauncherModel
from .widgets import Button, ListBox, TextField

MESSAGE_COLORS = {
    MessageLevel.INFO: INFO_COLOR,
    MessageLevel.SUCCESS: SUCCESS_COLOR,
    MessageLevel.WARNING: WARNING_COLOR,
    MessageLevel.ERROR: ERROR_COLOR,
}
MARGIN = 20
HEADER_HEIGHT = 84
FOOTER_HEIGHT = 60
LABEL_HEIGHT = 24
FIELD_HEIGHT = 32
SIZE_FIELD_WIDTH = 80
SHEET_LIST_ROWS = 5
TITLE_FONT_SIZE = 28
NEW_MAP_LABEL = "+  New map"


def is_digit(character: str) -> bool:
    return character.isdigit()


class LauncherView:
    """Window shown before the editor: map list, map settings and tileset."""

    def __init__(
        self,
        model: LauncherModel,
        on_submit: Callable[[], None],
        on_quit: Callable[[], None],
        size: Tuple[int, int],
    ) -> None:
        self.model = model
        self.screen = pygame.display.set_mode(size, pygame.RESIZABLE)
        pygame.display.set_caption("SuperMarioBros3 - Map editor")
        self.font = pygame.font.SysFont("Arial", FONT_SIZE)
        self.title_font = pygame.font.SysFont("Arial", TITLE_FONT_SIZE, bold=True)

        self.map_list = ListBox(self._map_items, self.selected_map_item, self._select_map_item)
        self.sheet_list = ListBox(self._sheet_items, lambda: model.sheet_index, model.select_sheet)
        self.name_field = TextField(
            lambda: model.name,
            lambda text: setattr(model, "name", text),
            allowed=lambda c: c.isalnum() or c in "-_",
            placeholder="level_2",
            is_enabled=lambda: model.is_new,
        )
        self.width_field = TextField(
            lambda: model.width, lambda text: setattr(model, "width", text), is_digit, 4
        )
        self.height_field = TextField(
            lambda: model.height, lambda text: setattr(model, "height", text), is_digit, 4
        )
        self.fields = [self.name_field, self.width_field, self.height_field]
        self.screen_button = Button(
            "1 screen", lambda: self._set_size(DEFAULT_MAP_SIZE)
        )
        self.quit_button = Button("Quit  (Esc)", on_quit)
        self.submit_button = Button(self._submit_label, on_submit)
        self.buttons = [self.screen_button, self.quit_button, self.submit_button]

        self.left_rect = pygame.Rect(0, 0, 0, 0)
        self.right_rect = pygame.Rect(0, 0, 0, 0)
        self.preview_rect = pygame.Rect(0, 0, 0, 0)
        self.labels: List[Tuple[str, Tuple[int, int]]] = []
        self._previews: Dict[Path, Optional[pygame.Surface]] = {}
        self.layout(self.screen.get_size())

    def layout(self, size: Tuple[int, int]) -> None:
        width, height = size
        top = HEADER_HEIGHT
        bottom = height - FOOTER_HEIGHT
        left_width = int((width - 3 * MARGIN) * 0.4)
        self.left_rect = pygame.Rect(MARGIN, top, left_width, bottom - top)
        self.right_rect = pygame.Rect(self.left_rect.right + MARGIN, top, width - left_width - 3 * MARGIN, bottom - top)

        self.labels = [("Maps  (res/maps)", (self.left_rect.x, top))]
        self.map_list.rect = pygame.Rect(
            self.left_rect.x, top + LABEL_HEIGHT, left_width, bottom - top - LABEL_HEIGHT
        )

        x, y = self.right_rect.x, top
        self.labels.append(("Map name", (x, y)))
        self.name_field.rect = pygame.Rect(x, y + LABEL_HEIGHT, self.right_rect.width, FIELD_HEIGHT)
        y = self.name_field.rect.bottom + 12

        self.labels.append(("Size in tiles (width x height)", (x, y)))
        y += LABEL_HEIGHT
        self.width_field.rect = pygame.Rect(x, y, SIZE_FIELD_WIDTH, FIELD_HEIGHT)
        self.labels.append(("x", (self.width_field.rect.right + 8, y + 6)))
        self.height_field.rect = pygame.Rect(self.width_field.rect.right + 24, y, SIZE_FIELD_WIDTH, FIELD_HEIGHT)
        self.screen_button.rect = pygame.Rect(self.height_field.rect.right + 12, y, 100, FIELD_HEIGHT)
        self.size_hint_position = (x, self.width_field.rect.bottom + 6)
        y = self.width_field.rect.bottom + 12 + LABEL_HEIGHT

        self.labels.append(("Tileset  (res/sheets)", (x, y)))
        list_height = SHEET_LIST_ROWS * self.sheet_list.item_height
        self.sheet_list.rect = pygame.Rect(x, y + LABEL_HEIGHT, self.right_rect.width, list_height)
        y = self.sheet_list.rect.bottom + 10
        self.preview_rect = pygame.Rect(x, y, self.right_rect.width, max(bottom - y, 0))

        button_y = bottom + (FOOTER_HEIGHT - BUTTON_HEIGHT - 4) // 2
        self.submit_button.rect = pygame.Rect(width - MARGIN - 170, button_y, 170, BUTTON_HEIGHT + 4)
        self.quit_button.rect = pygame.Rect(self.submit_button.rect.x - 12 - 120, button_y, 120, BUTTON_HEIGHT + 4)
        self.message_rect = pygame.Rect(MARGIN, bottom, self.quit_button.rect.x - 2 * MARGIN, FOOTER_HEIGHT)

        if self.model.selected is not None:
            self.map_list.ensure_visible(self.model.selected + 1)
        self.sheet_list.ensure_visible(self.model.sheet_index)

    def draw(self, mouse: Tuple[int, int], time: float) -> None:
        surface = self.screen
        surface.fill(BACKGROUND_COLOR)
        surface.blit(self.title_font.render("SuperMarioBros3  -  Map editor", True, TEXT_COLOR), (MARGIN, 14))
        surface.blit(
            self.font.render("Choose a map to edit, or create a new one.", True, MUTED_TEXT_COLOR),
            (MARGIN, 14 + self.title_font.get_linesize()),
        )
        for text, position in self.labels:
            surface.blit(self.font.render(text, True, TEXT_COLOR), position)

        self.map_list.draw(surface, self.font, mouse)
        self.sheet_list.draw(surface, self.font, mouse)
        for field in self.fields:
            field.draw(surface, self.font, time)
        for button in self.buttons:
            button.draw(surface, self.font, mouse)
        hint, color = self._size_hint()
        surface.blit(self.font.render(hint, True, color), self.size_hint_position)
        self._draw_preview(surface)

        pygame.draw.line(surface, BORDER_COLOR, (0, self.message_rect.y), (surface.get_width(), self.message_rect.y))
        if self.model.message:
            message = self.font.render(self.model.message, True, MESSAGE_COLORS[self.model.message_level])
            surface.set_clip(self.message_rect)
            surface.blit(message, message.get_rect(midleft=(self.message_rect.x, self.message_rect.centery)))
            surface.set_clip(None)
        pygame.display.flip()

    def _draw_preview(self, surface: pygame.Surface) -> None:
        sheet = self.model.sheet
        rect = self.preview_rect
        if sheet is None or rect.height < 16:
            return
        pygame.draw.rect(surface, PANEL_COLOR, rect, border_radius=4)
        image = self._preview(sheet.path)
        if image is None:
            return
        scale = max(min(rect.width // image.get_width(), rect.height // image.get_height(), 4), 1)
        scaled = pygame.transform.scale(image, (image.get_width() * scale, image.get_height() * scale))
        surface.set_clip(rect)
        surface.blit(scaled, scaled.get_rect(center=rect.center))
        surface.set_clip(None)

    def _preview(self, path: Path) -> Optional[pygame.Surface]:
        if path not in self._previews:
            try:
                color_key, _ = Tileset.settings_of(path, self.model.ressources_file)
                image = pygame.image.load(path)
                if color_key is not None:
                    image.set_colorkey(color_key)
            except (pygame.error, OSError):
                image = None
            self._previews[path] = image
        return self._previews[path]

    def _size_hint(self) -> Tuple[str, Tuple[int, int, int]]:
        if self.model.is_new:
            name = self.model.name or "<name>"
            return f"Will be created as res/maps/{name}.json", MUTED_TEXT_COLOR
        if self.model.resizes:
            return "The map will be resized (content outside is dropped on save)", WARNING_COLOR
        return "29x15 tiles = one game screen", MUTED_TEXT_COLOR

    def _submit_label(self) -> str:
        if self.model.is_new:
            return "Create  (Enter)"
        return "Open and resize" if self.model.resizes else "Open  (Enter)"

    def _set_size(self, size: Tuple[int, int]) -> None:
        self.model.width, self.model.height = (str(value) for value in size)

    def _map_items(self) -> List[Tuple[str, str]]:
        items = [(NEW_MAP_LABEL, "")]
        for entry in self.model.maps:
            detail = "unreadable" if entry.error else "{}x{}".format(*entry.size)
            items.append((entry.path.stem, detail))
        return items

    def selected_map_item(self) -> int:
        return 0 if self.model.selected is None else self.model.selected + 1

    def _select_map_item(self, index: int) -> None:
        if index == 0:
            self.model.select_new()
        else:
            self.model.select_map(index - 1)
        self.sheet_list.ensure_visible(self.model.sheet_index)

    def _sheet_items(self) -> List[Tuple[str, str]]:
        return [
            (sheet.path.name, "tileset" if sheet.has_metadata else "no metadata")
            for sheet in self.model.sheets
        ]
