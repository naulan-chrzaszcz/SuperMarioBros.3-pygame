from dataclasses import dataclass

from pygame.sprite import LayeredUpdates

from src.entities.player.player import Player
from src.maps_engine.camera import Camera
from src.maps_engine.type_of_map import TypeOfMap


@dataclass
class Map:
    name: str
    type: TypeOfMap
    camera: Camera
    player: Player
    data: LayeredUpdates
