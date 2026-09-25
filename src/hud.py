from __future__ import annotations

from pygame import Surface

from .font import Font
from .inputs.save import Save


class HUD:
    """Status bar at the bottom of the screen: world, lives, score, coins..."""

    WIDTH = 250
    HEIGHT = 30
    SCORE_DIGITS = 7

    def __init__(self, sheet: Surface, font: Font, save: Save):
        self.font = font
        self.image = Surface((self.WIDTH, self.HEIGHT))
        self.frame = sheet.subsurface((0, 0), (154, 30))
        # TODO: get inventory icons
        self.inventory = sheet.subsurface((155, 0), (74, 30))
        self.player_icon = sheet.subsurface((0, 31), (18, 9))
        speed = sheet.subsurface((19, 31), (53, 9))
        # TODO: animate the speed of the player
        self.speeds = [speed.subsurface((27, 0), (8, 9))] * 5 + [speed.subsurface((27, 0), (26, 9))]
        self.refresh(save)

    def get_width(self) -> int:
        return self.WIDTH

    def get_height(self) -> int:
        return self.HEIGHT

    def refresh(self, save: Save, timer: int = 0) -> None:
        """Redraws the values; call it when the save changes."""
        game = save.game
        render = self.font.render
        self.image.fill((0, 0, 0))
        self.image.blit(self.frame, (0, 0))
        self.image.blit(self.inventory, (self.WIDTH - self.inventory.get_width(), 0))
        self.image.blit(render(game.world), (36, 8))
        self.image.blit(render(game.coins), (141, 8))
        self.image.blit(self.player_icon, (4, 15))
        self.image.blit(render(game.life), (36, 16))
        self.image.blit(render(str(game.score).zfill(self.SCORE_DIGITS)), (50, 16))
        self.image.blit(render(str(timer).zfill(3)), (125, 16))
        for index, speed in enumerate(self.speeds):
            self.image.blit(speed, (50 + index * 8, 7))
