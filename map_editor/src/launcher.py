"""Launcher window loop that chooses a map and starts the editor application."""

from typing import Optional, Tuple

import pygame

from .constantes import FRAMERATE_LIMIT, LAUNCHER_WINDOW_SIZE
from .controllers.launcher_controller import LauncherController
from .models import MessageLevel
from .models.launcher_model import LauncherModel, LaunchRequest
from .views.launcher_view import LauncherView


class MapEditorLauncher:
    """First window of the editor: lets the user pick or create a map."""

    def __init__(
        self,
        model: Optional[LauncherModel] = None,
        window_size: Tuple[int, int] = LAUNCHER_WINDOW_SIZE,
        message: Optional[str] = None,
    ) -> None:
        self.model = model or LauncherModel()
        if message:
            self.model.notify(message, MessageLevel.ERROR)
        self.controller = LauncherController(self.model)
        self.view = LauncherView(self.model, self.controller.submit, self.controller.quit, window_size)
        self.controller.view = self.view

    def run(self) -> Optional[LaunchRequest]:
        pygame.key.start_text_input()
        clock = pygame.time.Clock()
        while self.controller.running:
            self.step(pygame.event.get(), clock.tick(FRAMERATE_LIMIT) / 1000.0)
        return self.controller.result

    def step(self, events, dt: float) -> None:
        for event in events:
            self.controller.handle_event(event)
        self.controller.update(dt)
        if self.controller.running:
            self.view.draw(pygame.mouse.get_pos(), self.controller.time)
