class MapManager:
    maps = {}
    current = None
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MapManager, cls).__new__(cls)
        return cls._instance

    def register(self, name: str, _map) -> None:
        self.maps[name] = _map

    def change_map(self, name: str) -> None:
        self.current = self.maps[name]

    def update(self, dt: float) -> None:
        self.current.sprites.update(dt)

    def draw(self, surface) -> None:
        self.current.sprites.draw(surface)
