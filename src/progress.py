"""Progress for one level: practice uses a disposable copy of the saved game."""

from __future__ import annotations

from copy import deepcopy
from typing import Callable

from .inputs.save import Game, Save


class ProgressSession:
    """The only progress a level may change, separate from its scene and HUD."""

    def __init__(self, saved: Save, practice: bool, persist: Callable[[], None]):
        self.save = deepcopy(saved) if practice else saved
        self.practice = practice
        self.persist = persist

    @property
    def game(self) -> Game:
        return self.save.game

    @game.setter
    def game(self, value: Game) -> None:
        self.save.game = value

    def commit(self) -> None:
        """Only a real level commits progress; practice is discarded."""
        if not self.practice:
            self.persist()
