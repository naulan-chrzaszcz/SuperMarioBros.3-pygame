from fr.naulan.supermariobros.src.entities.entity import Entity
from fr.naulan.supermariobros.src.maps.orientation import Orientation


class Tile(Entity):
    orientation: Orientation

    def __init__(self,
                 sheet,
                 orientation: Orientation,
                 position,
                 *groups):
        super().__init__(sheet, position, *groups)

        self.orientation = orientation

