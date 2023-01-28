from dataclasses import dataclass

from fr.naulan.supermariobros.src.entities.player.inventory import Inventory
from fr.naulan.supermariobros.src.entities.player.state import State
from fr.naulan.supermariobros.src.position import Position


@dataclass
class Save(object):
    inventory: Inventory
    position: Position
    state: State
    coins: int
    score: int
    life: int
