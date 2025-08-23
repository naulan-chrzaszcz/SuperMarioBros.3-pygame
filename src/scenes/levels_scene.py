from enum import Enum, auto

import pygame

from ..tile import Tile
from ..entities.player import Player
from ..hud import HUD
from ..map_manager import MapManager
from .scene import Scene


class AnimationState(Enum):
    ENTER_WORLD = auto()
    DONE = auto()


class LevelsScene(Scene):
    duration = {AnimationState.ENTER_WORLD: 1}
    state = None

    def __init__(self):
        super().__init__()
        self.map_manager = MapManager()

        self.hud = HUD()
        self.hud_pos = pygame.Vector2(
            self.surface.get_width() / 2 - self.hud.get_width() / 2,
            self.surface.get_height() - self.hud.get_height(),
        )

        self.player_move_speed = 0.1
        self.player_move_timer = 1.0

        self.spiral_index = 0

    def on_enter(self):
        self.levels = pygame.Surface(
            (self.map_manager.current.width, self.map_manager.current.height)
        )
        self.levels_pos = pygame.Vector2(
            0, self.surface.get_height() / 2 - self.levels.get_height() / 2
        )

        for sprite in self.map_manager.current.sprites:
            # TODO: dirty code to find the start tile and level 1 tile
            match sprite.id:
                case "start":
                    self.player_start_pos = sprite.vector
                case "level1":
                    self.level_1_pos = sprite.vector
                case "level2":
                    self.level_2_pos = sprite.vector
                case "level3":
                    self.level_3_pos = sprite.vector
                case "level4":
                    self.level_4_pos = sprite.vector
                case "level5":
                    self.level_5_pos = sprite.vector
                case "level6":
                    self.level_6_pos = sprite.vector
        self.player = Player(
            self.map_manager.current.sprites, self.player_start_pos.copy()
        )
        self.player.current_animation = self.player.levels_animation
        self.player_start_move_pos = self.player.vector.copy()
        self.player_end_move_pos = self.player.vector.copy()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                if self.player.vector in [
                    self.level_1_pos,
                    self.level_2_pos,
                    self.level_3_pos,
                    self.level_4_pos,
                    self.level_5_pos,
                    self.level_6_pos,
                ]:
                    self.spiral_segments = self.generate_inverse_spiral_segments()
                    self.state = AnimationState.ENTER_WORLD

            if self.player_move_timer == 1.0:
                self.timer = 0
                self.player_start_move_pos = self.player.vector.copy()
                if event.key == pygame.K_z:
                    self.player_end_move_pos = pygame.Vector2(
                        self.player.vector.x, self.player.vector.y - Tile.HEIGHT
                    )
                if event.key == pygame.K_q:
                    self.player_end_move_pos = pygame.Vector2(
                        self.player.vector.x - Tile.WIDTH, self.player.vector.y
                    )
                if event.key == pygame.K_s:
                    self.player_end_move_pos = pygame.Vector2(
                        self.player.vector.x, self.player.vector.y + Tile.HEIGHT
                    )
                if event.key == pygame.K_d:
                    self.player_end_move_pos = pygame.Vector2(
                        self.player.vector.x + Tile.WIDTH, self.player.vector.y
                    )

    def update(self, dt):
        self.timer += dt

        match self.state:
            case None:
                self.map_manager.update(dt)
                # TODO: dirty, move this code to player ?
                if any(
                    self.player.rect.colliderect(tile.rect) and tile.collidable
                    for tile in self.map_manager.current.sprites
                    if tile != self.player
                ):
                    self.player_end_move_pos = self.player_start_move_pos.copy()

                self.player_move_timer = min(self.timer / self.player_move_speed, 1.0)
                self.player.vector = self.player_start_move_pos.lerp(
                    self.player_end_move_pos, self.player_move_timer
                )
            case AnimationState.ENTER_WORLD:
                if self.spiral_index < len(self.spiral_segments):
                    self.spiral_index += (
                        len(self.spiral_segments)
                        / self.duration[AnimationState.ENTER_WORLD]
                        + 1
                    ) * dt
                if self.timer >= self.duration[self.state]:
                    self.timer = 0
                    self.state = AnimationState.DONE
            case AnimationState.DONE:
                match self.player.vector:
                    case self.level_1_pos:
                        self.manager.change_scene("level_1")
                    case self.level_2_pos:
                        self.manager.change_scene("level_2")
                    case self.level_3_pos:
                        self.manager.change_scene("level_3")
                    case self.level_4_pos:
                        self.manager.change_scene("level_4")
                    case self.level_5_pos:
                        self.manager.change_scene("level_5")
                    case self.level_6_pos:
                        self.manager.change_scene("level_6")

    def draw(self):
        self.surface.fill((0, 0, 0))
        self.map_manager.draw(self.levels)

        if self.state == AnimationState.ENTER_WORLD:
            # source: ChatGPT
            for x, y, dx, dy in self.spiral_segments[: int(self.spiral_index)]:
                rect = pygame.Rect(
                    min(x, x + dx) * Tile.WIDTH,
                    min(y, y + dy) * Tile.HEIGHT,
                    (abs(dx) + 1) * Tile.WIDTH,
                    (abs(dy) + 1) * Tile.HEIGHT,
                )
                pygame.draw.rect(self.levels, (0, 0, 0), rect)
        self.surface.blit(self.levels, self.levels_pos)

        self.surface.blit(self.hud, self.hud_pos)

    def generate_inverse_spiral_segments(self):
        # source: ChatGPT
        left, right = 0, self.levels.get_width() // Tile.WIDTH - 1
        top, bottom = 0, self.levels.get_height() // Tile.HEIGHT - 1

        segments = []
        while left <= right and top <= bottom:
            segments.append((left, top, right - left, 0))
            top += 1

            if top <= bottom:
                segments.append((right, top, 0, bottom - top))
                right -= 1
            if left <= right:
                segments.append((right, bottom, left - right, 0))
                bottom -= 1
            if top <= bottom:
                segments.append((left, bottom, 0, top - bottom))
                left += 1

        return segments
