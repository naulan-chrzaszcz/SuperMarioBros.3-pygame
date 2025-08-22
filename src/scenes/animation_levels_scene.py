from enum import Enum, auto

import math

from pygame import Surface, Vector2, Rect, draw

from ..inputs.ressources import Ressources
from ..inputs.save import Save
from ..map_manager import MapManager
from ..animated_tile import AnimatedTile
from ..tile import Tile
from ..hud import HUD
from ..font import Font
from .scene import Scene


class AnimationState(Enum):
    PAUSE = auto()
    HORIZONTAL_SHRINK = auto()
    STARS = auto()
    DONE = auto()


class AnimationLevelsScene(Scene):
    duration = {
        AnimationState.PAUSE: 3,
        AnimationState.HORIZONTAL_SHRINK: 0.1,
        AnimationState.STARS: 1,
    }
    state = AnimationState.PAUSE

    def __init__(self):
        super().__init__()
        font = Font()
        save = Save()
        res = Ressources()
        self.map_manager = MapManager()

        self.mario = res["images"]["mario"].subsurface(
            (Tile.WIDTH, Tile.HEIGHT), (Tile.WIDTH, Tile.HEIGHT)
        )
        self.sheet = res["images"]["levels"]
        self.stars_sheet = res["images"]["stars"]

        self.game_level_name = font.render(save.game.level)
        self.game_life = font.render(f"{save.game.life} X")
        self.game_player = font.render(save.player.upper())

        self.surface_width_center = self.surface.get_width() / 2
        self.surface_height_center = self.surface.get_height() / 2

        self.hud = HUD()
        self.hud_pos = Vector2(
            self.surface_width_center - self.hud.get_width() / 2,
            self.surface.get_height() - self.hud.get_height(),
        )

    def on_enter(self):
        self.map_manager.change_map("levels")
        self.levels = Surface(
            (self.map_manager.current.width, self.map_manager.current.height)
        )
        self.levels_pos = Vector2(
            0, self.surface.get_height() / 2 - self.levels.get_height() / 2
        )

        self.stats = Surface((self.surface_width_center, self.surface_height_center))
        stats_width_center = self.stats.get_width() / 2
        stats_height_center = self.stats.get_height() / 2
        self.stats_pos = Vector2(
            self.surface_width_center - stats_width_center,
            self.surface_height_center - stats_height_center,
        )

        self.stats.fill((0, 0, 0))
        # TODO: Draw the same frame of HUD
        self.stats_background = Rect(
            16, 16, self.stats.get_width() - 32, self.stats.get_height() - 32
        )
        self.stats_frame = Rect(
            14, 14, self.stats.get_width() - 28, self.stats.get_height() - 28
        )
        draw.rect(self.stats, (255, 255, 255), self.stats_frame)
        draw.rect(self.stats, (175, 232, 226), self.stats_background)
        self.stats.blit(
            self.game_level_name,
            (stats_width_center - self.game_level_name.get_width() / 2, 32),
        )
        self.stats.blit(
            self.game_life,
            (
                self.stats.get_width() - self.game_life.get_width() - 40,
                stats_height_center - self.game_life.get_height() / 2,
            ),
        )
        self.stats.blit(
            self.game_player,
            (32, stats_height_center - self.game_player.get_height() / 2),
        )
        self.stats.blit(
            self.mario,
            (
                self.stats.get_width() - 32,
                stats_height_center - self.mario.get_height() / 2,
            ),
        )

        self.stats_shrink_start_pos = Vector2(
            self.stats.get_width(), self.stats.get_height()
        )
        self.stats_shrink_end_pos = Vector2(0, self.stats.get_height())
        self.stats_shrink_current_pos = self.stats_shrink_start_pos.copy()

        self.stars_start_pos = Vector2(
            self.levels.get_width() / 2, self.levels.get_height() / 2
        )
        self.stars_levels = []
        for _ in range(8):
            pos = self.stars_start_pos.copy()
            self.stars_levels.append(
                AnimatedTile(
                    self.stars_sheet, pos, 4, speed=4, tile_width=11, tile_height=11
                )
            )
        self.stars_max_radius = 100
        self.stars_speed = 2 * math.pi / self.duration[AnimationState.STARS]
        self.stars_angle = 0
        self.star_angles = [
            i * (2 * math.pi / len(self.stars_levels))
            for i in range(len(self.stars_levels))
        ]

        for tile in self.map_manager.current.tiles:
            # TODO: Dirty code to find the start tile
            if tile.vector.x == Tile.WIDTH * 3 and tile.vector.y == Tile.HEIGHT * 5:
                self.stars_end_pos = tile.vector

    def update(self, dt):
        self.timer += dt
        self.map_manager.update(dt)

        match self.state:
            case AnimationState.PAUSE:
                if self.timer >= self.duration[self.state]:
                    self.timer = 0
                    self.state = AnimationState.HORIZONTAL_SHRINK
            case AnimationState.HORIZONTAL_SHRINK:
                t = min(self.timer / self.duration[self.state], 1.0)
                self.stats_shrink_current_pos = self.stats_shrink_start_pos.lerp(
                    self.stats_shrink_end_pos, t
                )
                if self.timer >= self.duration[self.state]:
                    self.timer = 0
                    self.state = AnimationState.STARS
            case AnimationState.STARS:
                self.stars_angle += self.stars_speed * dt
                t = min(self.timer / self.duration[self.state], 1.0)
                self.radius = math.sin(t * math.pi) * self.stars_max_radius
                for i, star in enumerate(self.stars_levels):
                    theta = self.stars_angle + self.star_angles[i]

                    base_pos = self.stars_start_pos.lerp(self.stars_end_pos, t)
                    x = base_pos.x + self.radius * math.cos(theta)
                    y = base_pos.y + self.radius * math.sin(theta)

                    star.vector.update(x, y)
                    star.update(dt)

                if self.timer >= self.duration[self.state]:
                    self.timer = 0
                    self.state = AnimationState.DONE
            case AnimationState.DONE:
                # TODO
                pass

    def draw(self):
        self.surface.fill((0, 0, 0))
        self.map_manager.draw(self.levels)

        if self.state == AnimationState.STARS:
            for star in self.stars_levels:
                star.draw(self.levels)

        self.surface.blit(self.levels, self.levels_pos)
        if self.state != AnimationState.STARS:
            stats = self.stats.subsurface((0, 0), self.stats_shrink_current_pos)
            self.surface.blit(stats, self.stats_pos)
        self.surface.blit(self.hud, self.hud_pos)
