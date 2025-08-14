from typing import Protocol

from ..display import Display
from ..scene_manager import SceneManager


class Scene(Protocol):
    def __init__(self):
        super().__init__()
        self.manager = SceneManager()
        self.surface = Display()
        self.timer = 0.0

    def handle_event(self, event: list): ...
    def update(self, dt: float): ...
    def draw(self): ...
    def on_enter(self): ...
    def on_exit(self): ...
