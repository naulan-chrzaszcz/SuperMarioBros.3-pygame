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
        for tile in self.current.animated_tiles:
            tile.update(dt)

    def draw(self, surface) -> None:
        for tile in self.current.tiles:
            tile.draw(surface)
        for tile in self.current.animated_tiles:
            tile.draw(surface)
