from dataclasses import dataclass

from pygame.sprite import LayeredUpdates

from src.entities.player.player import Player
from src.maps_engine.camera import Camera
from src.maps_engine.type_of_map import TypeOfMap


@dataclass
class Map:
    """
        Store all datas about a map/level
    """
    # Name of the map/level
    name: str
    # Normal map or specific context map
    type: TypeOfMap
    # The camera linked to the map
    camera: Camera
    # The player linked to the map
    player: Player
    # The list of entities
    data: LayeredUpdates
