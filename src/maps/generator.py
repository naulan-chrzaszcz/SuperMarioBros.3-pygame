from typing import List, Union

from pygame.sprite import LayeredUpdates

from src.entities.entity import Entity
from src.entities.position import Position
from src.maps.type_of_tile import TypeOfTile
from src.maps.camera import Camera
from src.maps.map import Map
from src.maps.type_of_map import TypeOfMap

class MapsGenerator(object):
    TILE_SIZE = 16
    SEPARATOR = ','

    data = list()

    def new(self, raw_data: Union[str, List], name: str, have_header: bool = True) -> None:
        lines = raw_data.splitlines() if isinstance(raw_data, str) else raw_data
        tile_width = len(lines[0 if not have_header else 1].split(MapsGenerator.SEPARATOR))
        tile_height = len(lines) - (1 if have_header else 0)

        # Load camera
        camera = Camera((tile_width * self.TILE_SIZE, tile_height * self.TILE_SIZE))

        type_of_map = None
        if have_header:
            var, val = lines[0].split(':')
            match var:
                case "type_of_map":
                    type_of_map = TypeOfMap(int(val))
                case _:
                    pass

        player = None
        entities = LayeredUpdates()
        for y, line in enumerate(lines[0:] if have_header else lines):
            tiles = line.split(MapsGenerator.SEPARATOR)
            for x, tile in enumerate(tiles):
                tile = int(tile)
                if tile != TypeOfTile.EMPTY.value:
                    position = Position(x * self.TILE_SIZE, y * self.TILE_SIZE)
                    match tile:
                        case Entity.PLAYER:
                            player = Entity(None, position, entities)
                        case _:
                            Entity(None, position, entities)

        self.data.append(Map(name, type_of_map, camera, player, entities))


