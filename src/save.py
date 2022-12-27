from dataclasses import dataclass

from src.entities.player.inventory import Inventory
from src.entities.player.state import State
from src.position import Position


@dataclass
class Save(object):
    inventory: Inventory
    position: Position
    state: State
    coins: int
    score: int
    life: int
