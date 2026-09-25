"""Runs the map editor inside the game window.

The editor (``map_editor/``) keeps its own loops: the launcher, then the
editor of a map. When the user asks to play the map (F5), the editor is left,
the game plays the map, and the same editor comes back afterwards with its
undo history and clipboard.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pygame
import yaml

EDITOR_KEY_REPEAT = (250, 35)


@dataclass(frozen=True)
class EditorResult:
    # The window was closed: the whole game quits.
    quit: bool = False
    # Map to play (already saved), None when the editor was only left.
    map_path: Optional[Path] = None
    sheet_path: Optional[Path] = None

    @property
    def play(self) -> bool:
        return self.map_path is not None


class EditorSession:
    def __init__(self):
        self.application = None
        self.clipboard = None
        self.message: Optional[str] = None

    @property
    def paused(self) -> bool:
        """True while the game plays the map being edited."""
        return self.application is not None

    def run(self) -> EditorResult:
        """Shows the editor until it is left; blocks like a game loop."""
        pygame.key.set_repeat(*EDITOR_KEY_REPEAT)
        pygame.mouse.set_visible(True)
        try:
            if self.application is not None:
                application, self.application = self.application, None
                application.resume()
                result = self._run(application)
                if result is not None:
                    return result
            return self._run_launcher()
        finally:
            pygame.key.stop_text_input()
            pygame.key.set_repeat(0)

    def _run_launcher(self) -> EditorResult:
        from map_editor.src.application import MapEditorApplication
        from map_editor.src.launcher import MapEditorLauncher

        while True:
            launcher = MapEditorLauncher(message=self.message)
            self.message = None
            request = launcher.run()
            if request is None:
                return EditorResult(quit=launcher.controller.window_closed)
            try:
                application = MapEditorApplication(
                    request.map_path,
                    request.sheet_path,
                    request.size,
                    clipboard=self.clipboard,
                    playable=True,
                )
            except (OSError, ValueError, pygame.error, yaml.YAMLError) as error:
                self.message = f"Cannot open {request.map_path.name}: {error}"
                continue
            result = self._run(application)
            if result is not None:
                return result

    def _run(self, application) -> Optional[EditorResult]:
        """Runs one map; None when it was closed to go back to the launcher."""
        application.run()
        self.clipboard = application.state.clipboard
        controller = application.controller
        if controller.window_closed:
            return EditorResult(quit=True)
        if controller.play_requested:
            self.application = application
            return EditorResult(map_path=application.map_path, sheet_path=application.tileset.sheet_path)
        return None
