from entities.entity import Entity
from maps.orientation import Orientation


class Tile(Entity):
    orientation: Orientation

    def __init__(self,
                 sheet,
                 orientation: Orientation,
                 position,
                 *groups):
        super().__init__(sheet, position, *groups)

        self.orientation = orientation

