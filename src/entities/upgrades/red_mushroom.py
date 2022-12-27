from src.entities.upgrades.upgrade import Upgrade


class RedMushroom(Upgrade):

    def __init__(self, group_sprites, game, position) -> None:
        Upgrade.__init__(self, group_sprites, game, position)

    def apply(self) -> None:
        pass

    def update(self, *args, **kwargs) -> None:
        pass
