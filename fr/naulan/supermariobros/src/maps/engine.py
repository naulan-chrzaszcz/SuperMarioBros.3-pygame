from typing import List, Union

from pygame.sprite import LayeredUpdates

from fr.naulan.supermariobros.src.entities.entity import Entity
from fr.naulan.supermariobros.src.entities.player import Player
from fr.naulan.supermariobros.src.entities.position import Position
from fr.naulan.supermariobros.src.maps.tiles import Tiles
from fr.naulan.supermariobros.src.maps.camera import Camera
from fr.naulan.supermariobros.src.maps.map import Map
from fr.naulan.supermariobros.src.maps.type_of_map import TypeOfMap


class MapsEngine(object):
    data: List = list()

    @staticmethod
    def get_maps_separator() -> str: return ','

    def new(self, raw_data: Union[str, List], name: str, header: bool = True) -> None:
        # Knowing the map size
        if isinstance(raw_data, str):
            lines = raw_data.splitlines()
        else:
            lines = raw_data
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
                type_of_tile = int(col)
                if type_of_tile != Tiles.EMPTY:
                    position = Position(x * 16, y * 16)
                    # sheet = self.game.gallery.get(int(col))     # TODO Improve this
                    if len(col) >= 3:
                        orientation = int(col[1])
                        color_of_tile = str(col[2])
                        if type_of_tile == Tiles.PLATFORM:
                            if color_of_tile == 1:
                                pass
                    else:
                        if len(col) == 1:
                            if int(col) == Entity.PLAYER:
                                player = Player(None, position, sprites)

        self.data.append(Map(name, type_of_map, camera, player, sprites))
