"""Controller for launcher form events and map opening requests."""

from __future__ import annotations

from typing import Optional

import pygame

from ..models import MessageLevel
from ..models.launcher_model import LauncherModel, LaunchRequest
from ..views.launcher_view import LauncherView

DOUBLE_CLICK_DELAY = 0.4


class LauncherController:
    """Keyboard and mouse handling of the launcher window."""

    def __init__(self, model: LauncherModel) -> None:
        self.model = model
        self.view: Optional[LauncherView] = None
        self.running = True
        self.result: Optional[LaunchRequest] = None
        # True when the window was closed rather than the launcher left.
        self.window_closed = False
        self.time = 0.0
        self._last_click = (-1, -1.0)

    def update(self, dt: float) -> None:
        self.time += dt

    def submit(self) -> None:
        try:
            self.result = self.model.request()
        except (OSError, ValueError) as error:
            self.model.notify(str(error), MessageLevel.ERROR)
            return
        self.running = False

    def quit(self) -> None:
        self.result = None
        self.running = False

    def handle_event(self, event: pygame.event.Event) -> None:
        view = self.view
        if not self.running:
            return
        if event.type == pygame.QUIT:
            self.window_closed = True
            self.quit()
        elif event.type == pygame.VIDEORESIZE:
            view.layout(view.screen.get_size())
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._click(event.pos)
        elif event.type == pygame.MOUSEWHEEL:
            mouse = pygame.mouse.get_pos()
            for list_box in (view.map_list, view.sheet_list):
                if list_box.rect.collidepoint(mouse):
                    list_box.scroll_by(-event.y)
        elif event.type == pygame.TEXTINPUT:
            self._focused_field_event(event)
        elif event.type == pygame.KEYDOWN:
            self._key(event)

    def _click(self, position) -> None:
        view = self.view
        for button in view.buttons:
            if button.click(position):
                return
        for field in view.fields:
            field.focused = field.rect.collidepoint(position) and field.is_enabled()

        index = view.map_list.click(position)
        if index is not None:
            last_index, last_time = self._last_click
            if index == last_index and self.time - last_time <= DOUBLE_CLICK_DELAY:
                self.submit()
                return
            self._last_click = (index, self.time)
            if self.model.is_new:
                self._focus(view.name_field)
            return
        view.sheet_list.click(position)

    def _key(self, event) -> None:
        view = self.view
        if event.key == pygame.K_ESCAPE:
            self.quit()
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.submit()
        elif event.key == pygame.K_TAB:
            enabled = [field for field in view.fields if field.is_enabled()]
            current = next((i for i, field in enumerate(enabled) if field.focused), -1)
            step = -1 if event.mod & pygame.KMOD_SHIFT else 1
            self._focus(enabled[(current + step) % len(enabled)])
        elif event.key in (pygame.K_UP, pygame.K_DOWN):
            count = len(self.model.maps) + 1
            current = view.selected_map_item()
            index = (current + (1 if event.key == pygame.K_DOWN else -1)) % count
            view.map_list.on_select(index)
            view.map_list.ensure_visible(index)
            if not self.model.is_new:
                self._focus(None)
        else:
            self._focused_field_event(event)

    def _focus(self, focused) -> None:
        for field in self.view.fields:
            field.focused = field is focused

    def _focused_field_event(self, event) -> None:
        for field in self.view.fields:
            if field.handle_event(event):
                return
