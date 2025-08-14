from pygame import Surface

from .font import Font
from .inputs.ressources import Ressources
from .inputs.save import Save


class HUD(Surface):
    _instance = None

    def __init__(self):
        super().__init__((250, 30))
        font = Font()
        save = Save()

        sheet = Ressources()["images"]["hud"]
        hud = sheet.subsurface((0, 0), (154, 30))
        # TODO: get inventory icons
        inventory = sheet.subsurface((155, 0), (74, 30))
        player_icon = sheet.subsurface((0, 31), (18, 9))
        speed = sheet.subsurface((19, 31), (53, 9))
        # TODO: animate the speed of the player
        speeds = [speed.copy().subsurface((27, 0), (8, 9)) for _ in range(5)]
        speeds.append(speed.copy().subsurface((27, 0), (26, 9)))

        # TODO: need to be updated
        world = font.render(save.game.level.split(" ")[1])
        life = font.render(save.game.life)
        coins = font.render(save.game.coins)
        score = font.render(
            "0" * max(0, 7 - len(str(save.game.score))) + str(save.game.score)
        )
        # TODO: do the timer of levels
        timer = font.render("000")

        self.blit(hud, (0, 0))
        self.blit(inventory, (self.get_width() - 74, 0))
        self.blit(world, (36, 8))
        self.blit(coins, (141, 8))
        self.blit(player_icon, (4, 15))
        self.blit(life, (36, 16))
        self.blit(score, (50, 16))
        self.blit(timer, (125, 16))
        for n, _speed in enumerate(speeds):
            self.blit(_speed, (50 + n * 8, 7))

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(HUD, cls).__new__(cls)
        return cls._instance

    def update(self):
        # TODO
        pass
