from fr.naulan.supermariobros.src.entities.entity import Entity


class Player(Entity):

    def __init__(self, sheet, position, *groups):
        super().__init__(sheet, position, *groups)

