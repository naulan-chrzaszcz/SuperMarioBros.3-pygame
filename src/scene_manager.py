from pygame import QUIT


class SceneManager:
    scenes = {}
    current = None
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SceneManager, cls).__new__(cls)
        return cls._instance

    def register(self, name: str, scene) -> None:
        self.scenes[name] = scene

    def change_scene(self, name: str) -> None:
        self.current.on_exit()
        self.current = self.scenes[name]
        self.current.on_enter()

    def set_default_scene(self, name: str) -> None:
        self.current = self.scenes[name]
        self.current.on_enter()

    def handle_events(self, events) -> None:
        for event in events:
            if event.type == QUIT:
                quit()
            self.current.handle_event(event)

    def update(self, dt: float) -> None:
        self.current.update(dt)

    def draw(self) -> None:
        self.current.draw()
