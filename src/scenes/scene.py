from ..display import Display
from ..scene_manager import SceneManager


class Scene:
    def __init__(self):
        self.manager = SceneManager()
        self.surface = Display()
        self.timer = 0.0

    def handle_event(self, event: list): pass
    def update(self, dt: float): pass
    def draw(self): pass
    def on_enter(self): pass
    def on_exit(self): pass
