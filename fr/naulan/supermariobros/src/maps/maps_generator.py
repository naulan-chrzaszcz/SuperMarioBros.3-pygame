from typing import List, Union

from pygame.sprite import LayeredUpdates

from fr.naulan.supermariobros.src.entities.entity import Entity
from fr.naulan.supermariobros.src.entities.player import Player
from fr.naulan.supermariobros.src.entities.position import Position
from fr.naulan.supermariobros.src.maps.type_of_tile import TypeOfTile
from fr.naulan.supermariobros.src.maps.camera import Camera
from fr.naulan.supermariobros.src.maps.map import Map
from fr.naulan.supermariobros.src.maps.type_of_map import TypeOfMap


class MapsGenerator(object):
    SEPARATOR = ','

    data = list()

    def new(self, raw_data: Union[str, List], name: str, have_header: bool = True) -> None:
        lines = raw_data.splitlines() if isinstance(raw_data, str) else raw_data
        tile_width = len(lines[0 if not have_header else 1].split(MapsGenerator.SEPARATOR))
        tile_height = len(lines)

        # Load camera
        camera = Camera((tile_width * 16, tile_height * 16))

        type_of_map = None
        if have_header:
            var, val = lines[0].split(':')
            match var:
                case "type_of_map":
                    type_of_map = TypeOfMap(int(val))
                case _:
                    pass

        player = None
        sprites = LayeredUpdates()
        for y, line in enumerate(lines[0:] if have_header else lines):
            columns = line.split(MapsGenerator.SEPARATOR)
            for x, col in enumerate(columns):
                type_of_tile = int(col)
                if type_of_tile != TypeOfTile.EMPTY:
                    position = Position(x * 16, y * 16)
                    # sheet = self.game.gallery.get(int(col))     # TODO Improve this
                    if len(col) >= 3:
                        orientation = int(col[1])
                        color_of_tile = str(col[2])
                        if type_of_tile == TypeOfTile.PLATFORM:
                            if color_of_tile == 1:
                                pass
                    else:
                        if len(col) == 1:
                            if int(col) == Entity.PLAYER:
                                player = Player(None, position, sprites)

        self.data.append(Map(name, type_of_map, camera, player, sprites))
