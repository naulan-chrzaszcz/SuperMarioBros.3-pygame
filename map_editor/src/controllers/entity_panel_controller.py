"""Controller of the panel that tunes one entity placed on the map."""

from __future__ import annotations

import pygame

from ..models import EntityPanel
from ..views.entity_panel_view import EntityPanelView


class EntityPanelController:
    """Keyboard and mouse of the entity panel.

    Its methods return True when the event was for the panel: the rest of the
    editor then ignores it, so the arrow keys tune the entity instead of moving
    the view while the panel is open.
    """

    def __init__(self, panel: EntityPanel, view: EntityPanelView) -> None:
        self.panel = panel
        self.view = view

    def handle_key(self, event: pygame.event.Event) -> bool:
        if not self.view.visible or event.mod & pygame.KMOD_CTRL:
            return False
        key = event.key
        if key == pygame.K_ESCAPE:
            self.panel.close()
        elif key in (pygame.K_UP, pygame.K_DOWN):
            self.panel.select(self.panel.index + (1 if key == pygame.K_DOWN else -1))
        elif key in (pygame.K_LEFT, pygame.K_RIGHT):
            self.panel.change(1 if key == pygame.K_RIGHT else -1)
        elif key in (pygame.K_BACKSPACE, pygame.K_DELETE):
            self.panel.reset()
        else:
            return False
        return True

    def handle_mouse(self, event: pygame.event.Event) -> bool:
        if not self.view.visible:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.view.click(event.pos)
        # A click through the panel would paint on the map below it.
        return event.type != pygame.MOUSEMOTION and self.view.hovered(getattr(event, "pos", None))

    def handle_wheel(self, event: pygame.event.Event, mouse) -> bool:
        if not event.y:
            return False
        return self.view.scroll(-1 if event.y > 0 else 1, mouse)
