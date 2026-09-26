from __future__ import annotations

from pygame import Surface

from .animation import SpriteBank
from .font import Font
from .inputs.save import Save


class HUD:
    """Status bar at the bottom of the screen: world, lives, score, coins...

    Its pictures and the place of each value are the ``hud`` sprite of
    ``res/sprites.yaml``.
    """

    SPRITE = "hud"
    WIDTH = 250
    HEIGHT = 30
    SCORE_DIGITS = 7
    SPEED_ARROWS = 5

    def __init__(self, sprites: SpriteBank, font: Font, save: Save):
        self.font = font
        self.image = Surface((self.WIDTH, self.HEIGHT))
        self.frame = sprites.image(self.SPRITE, "frame")
        # TODO: get inventory icons
        self.inventory = sprites.image(self.SPRITE, "inventory")
        self.player_icon = sprites.image(self.SPRITE, "player_icon")
        # TODO: animate the speed of the player
        self.speeds = [sprites.image(self.SPRITE, "speed_arrow")] * self.SPEED_ARROWS
        self.speeds.append(sprites.image(self.SPRITE, "speed_power"))
        self.positions = {
            name: sprites.position(self.SPRITE, name)
            for name in ("world", "coins", "player_icon", "lives", "score", "time", "speed")
        }
        self.refresh(save)

    def get_width(self) -> int:
        return self.WIDTH

    def get_height(self) -> int:
        return self.HEIGHT

    def refresh(self, save: Save, timer: int = 0) -> None:
        """Redraws the values; call it when the save changes."""
        game = save.game
        render = self.font.render
        at = self.positions
        self.image.fill((0, 0, 0))
        self.image.blit(self.frame, (0, 0))
        self.image.blit(self.inventory, (self.WIDTH - self.inventory.get_width(), 0))
        self.image.blit(render(game.world), at["world"])
        self.image.blit(render(game.coins), at["coins"])
        self.image.blit(self.player_icon, at["player_icon"])
        self.image.blit(render(game.life), at["lives"])
        self.image.blit(render(str(game.score).zfill(self.SCORE_DIGITS)), at["score"])
        self.image.blit(render(str(timer).zfill(3)), at["time"])
        x, y = at["speed"]
        for index, speed in enumerate(self.speeds):
            self.image.blit(speed, (x + index * 8, y))
