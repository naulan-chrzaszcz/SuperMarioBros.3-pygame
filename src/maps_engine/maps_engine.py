from typing import List

from pygame.sprite import LayeredUpdates

from src.entities.player.player import Player
from src.entities.coin import Coin
from src.game import Game
from src.maps_engine.tiles import Tiles
from src.maps_engine.camera import Camera
from src.maps_engine.map import Map
from src.maps_engine.type_of_map import TypeOfMap
from src.position import Position


class MapsEngine(object):
    maps: List[Map, ...]
    game: Game

    def __init__(self, game):
        self.game = game
        self.t = 0

    @staticmethod
    def get_maps_separator() -> str:
        return ','

    def new(self, raw_data: str, name: str, header: bool = True) -> None:
        # Knowing the map size
        lines = raw_data.splitlines()
        tile_width = len(lines[0 if not header else 1].split(MapsEngine.get_maps_separator()))
        tile_height = len(lines)

        # Load camera
        camera = Camera((tile_width * 16, tile_height * 16))

        type_of_map = None
        if header:
            header = lines[0].split(':')
            if header[0] in "type_of_map":
                if int(header[1]) == 1:
                    type_of_map = TypeOfMap.STAGE
                elif int(header[1]) == 2:
                    type_of_map = TypeOfMap.LEVEL

        player = None
        sprites = LayeredUpdates()
        for y, line in enumerate(lines[0:] if header else lines):
            columns = line.split(MapsEngine.get_maps_separator())
            for x, col in enumerate(columns):
                type_of_tile = int(col[0])
                if type_of_tile == Tiles.EMPTY:
                    position = Position(x * 16, y * 16)
                    sheet = self.game.gallery.get(int(col))
                    if len(col) >= 3:
                        orientation = int(col[1])
                        color_of_tile = int(col[2])
                        if type_of_tile == Tiles.PLATFORM:
                            if color_of_tile == 1:
                                pass
                    else:
                        if len(col) == 1:
                            if col in "0":
                                player = Player(sprites, sheet, position)
                            if col in "1":
                                Coin(sprites, sheet, position)
        self.maps.append(Map(name, type_of_map, camera, player, sprites))
