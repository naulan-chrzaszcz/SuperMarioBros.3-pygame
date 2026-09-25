from __future__ import annotations

import math
from enum import Enum, auto

from pygame import Rect, Surface, Vector2, draw

from ..constants import BLACK, STATS_BACKGROUND, WHITE
from ..entities.player import Player
from ..sprite_animation import SpriteAnimation
from ..tile import Tile
from .scene import GameContext, Scene


class AnimationState(Enum):
    PAUSE = auto()
    HORIZONTAL_SHRINK = auto()
    STARS = auto()
    DONE = auto()


class AnimationLevelsScene(Scene):
    """"WORLD 1 / MARIO x 4" card, then stars flying to the start of the map."""

    duration = {
        AnimationState.PAUSE: 3.0,
        AnimationState.HORIZONTAL_SHRINK: 0.1,
        AnimationState.STARS: 1.0,
    }
    STAR_COUNT = 8
    STAR_SIZE = 11
    STARS_MAX_RADIUS = 100

    def __init__(self, context: GameContext, map_name: str = "levels", next_scene: str = "levels"):
        super().__init__(context)
        self.map_name = map_name
        self.next_scene = next_scene

        width, height = self.surface.get_size()
        self.stats = Surface((width // 2, height // 2))
        stats_width, stats_height = self.stats.get_size()
        self.stats_pos = Vector2(width // 2 - stats_width // 2, height // 2 - stats_height // 2)
        self.stats_background = Rect(16, 16, stats_width - 32, stats_height - 32)
        # TODO: Draw the same frame of HUD
        self.stats_frame = Rect(14, 14, stats_width - 28, stats_height - 28)
        self.player = Player(
            (), Vector2(stats_width - 32, stats_height // 2 - Tile.HEIGHT // 2), context.ressources.image("mario")
        )
        self.stars_sheet = context.ressources.image("stars")

    def on_enter(self) -> None:
        super().on_enter()
        width, height = self.surface.get_size()
        font, save, hud = self.context.font, self.context.save, self.context.hud
        stats_width, stats_height = self.stats.get_size()
        self.state = AnimationState.PAUSE
        self.stats_shrink_width = stats_width

        self.game_level_name = font.render(save.game.level)
        self.game_level_name_pos = Vector2(32, 32)
        self.game_life = font.render(f"{save.game.life} X")
        self.game_life_pos = Vector2(
            stats_width - self.game_life.get_width() - 40, stats_height // 2 - self.game_life.get_height() // 2
        )
        self.game_player = font.render(save.player)
        self.game_player_pos = Vector2(32, stats_height // 2 - self.game_player.get_height() // 2)
        self.player.play(self.player.levels_animation)
        hud.refresh(save)
        self.hud_pos = Vector2(width // 2 - hud.get_width() // 2, height - hud.get_height())

        self.world = self.context.maps.change_map(self.map_name)
        self.levels = Surface((self.world.width, self.world.height))
        self.levels_pos = Vector2(0, height // 2 - self.levels.get_height() // 2)

        self.stars_start_pos = Vector2(self.levels.get_width() / 2, self.levels.get_height() / 2)
        start = self.world.find("start")
        self.stars_end_pos = start.vector.copy() if start is not None else self.stars_start_pos.copy()
        self.stars = []
        for _ in range(self.STAR_COUNT):
            star = Tile((), "star", self.stars_sheet, self.stars_start_pos, self.STAR_SIZE, self.STAR_SIZE)
            star.set_animation(SpriteAnimation(star, self.stars_sheet, 4, 4))
            self.stars.append(star)
        self.stars_speed = 2 * math.pi / self.duration[AnimationState.STARS]
        self.stars_angle = 0.0
        self.star_angles = [i * 2 * math.pi / self.STAR_COUNT for i in range(self.STAR_COUNT)]

    def _next_state(self, state: AnimationState) -> None:
        self.state = state
        self.timer = 0.0

    def update(self, dt: float) -> None:
        super().update(dt)
        self.world.update(dt)
        self.player.update(dt)

        if self.state == AnimationState.DONE:
            self.manager.change_scene(self.next_scene)
            return
        t = min(self.timer / self.duration[self.state], 1.0)
        if self.state == AnimationState.HORIZONTAL_SHRINK:
            self.stats_shrink_width = round(self.stats.get_width() * (1 - t))
        elif self.state == AnimationState.STARS:
            self.stars_angle += self.stars_speed * dt
            radius = math.sin(t * math.pi) * self.STARS_MAX_RADIUS
            centre = self.stars_start_pos.lerp(self.stars_end_pos, t)
            for star, angle in zip(self.stars, self.star_angles):
                theta = self.stars_angle + angle
                star.vector.update(centre.x + radius * math.cos(theta), centre.y + radius * math.sin(theta))
                star.update(dt)
        if t >= 1.0:
            self._next_state(list(AnimationState)[list(AnimationState).index(self.state) + 1])

    def draw(self) -> None:
        self.surface.fill(BLACK)
        self.world.draw(self.levels)
        if self.state == AnimationState.STARS:
            for star in self.stars:
                self.levels.blit(star.image, star.rect)
        self.surface.blit(self.levels, self.levels_pos)

        if self.state in (AnimationState.PAUSE, AnimationState.HORIZONTAL_SHRINK) and self.stats_shrink_width > 0:
            self.stats.fill(BLACK)
            draw.rect(self.stats, WHITE, self.stats_frame)
            draw.rect(self.stats, STATS_BACKGROUND, self.stats_background)
            self.stats.blit(self.game_level_name, self.game_level_name_pos)
            self.stats.blit(self.game_life, self.game_life_pos)
            self.stats.blit(self.game_player, self.game_player_pos)
            self.stats.blit(self.player.image, self.player.rect)
            stats = self.stats.subsurface((0, 0), (self.stats_shrink_width, self.stats.get_height()))
            self.surface.blit(stats, self.stats_pos)
        self.surface.blit(self.context.hud.image, self.hud_pos)
