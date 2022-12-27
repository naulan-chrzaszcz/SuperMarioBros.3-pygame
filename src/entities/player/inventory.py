from dataclasses import dataclass

from src.entities.upgrades.upgrade import Upgrade


@dataclass
class Inventory(object):
    SLOT_1: Upgrade = None
    SLOT_2: Upgrade = None
    SLOT_3: Upgrade = None
