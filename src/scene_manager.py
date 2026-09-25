from __future__ import annotations

from typing import Dict, Iterable, Optional

from pygame import QUIT
from pygame.event import Event


class SceneManager:
    """Runs one scene at a time.

    Changing scene is deferred to the end of the frame's update, so a scene is
    never left half updated and the new one is drawn only after ``on_enter``.
    """

    def __init__(self):
        self.scenes: Dict[str, object] = {}
        self.current = None
        self.current_name: Optional[str] = None
        self.running = True
        self._next: Optional[str] = None

    def register(self, name: str, scene) -> None:
        scene.manager = self
        self.scenes[name] = scene

    def has_scene(self, name: str) -> bool:
        return name in self.scenes

    def _check(self, name: str) -> None:
        if name not in self.scenes:
            raise KeyError(f"Unknown scene {name!r}; registered: {', '.join(self.scenes)}")

    def set_default_scene(self, name: str) -> None:
        self._check(name)
        self.current_name = name
        self.current = self.scenes[name]
        self.current.on_enter()

    def change_scene(self, name: str) -> None:
        self._check(name)
        self._next = name

    def quit(self) -> None:
        self.running = False

    def handle_events(self, events: Iterable[Event]) -> None:
        for event in events:
            if event.type == QUIT:
                self.quit()
            elif self.running:
                self.current.handle_event(event)

    def update(self, dt: float) -> None:
        self.current.update(dt)
        if self._next is not None:
            name, self._next = self._next, None
            self.current.on_exit()
            self.current_name = name
            self.current = self.scenes[name]
            self.current.on_enter()

    def draw(self) -> None:
        self.current.draw()
