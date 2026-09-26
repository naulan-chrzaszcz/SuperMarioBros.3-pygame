"""World map scene: draws the map, moves Mario (``world_map.py``) and opens levels."""

from __future__ import annotations

from enum import Enum, auto
from typing import List, Optional, Tuple

import pygame
from pygame import Rect, Surface, Vector2

from ..constants import BLACK, WHITE
from ..entities.player import Player
from ..inputs.config import Action
from ..inputs.tuning import tune
from ..tile import Tile
from ..world_map import DIRECTIONS, WorldMapWalker, level_scene_of
from .scene import GameContext, Scene

Segment = Tuple[int, int, int, int]


class AnimationState(Enum):
    ENTER_WORLD = auto()


def inverse_spiral_segments(columns: int, rows: int) -> List[Segment]:
    """Segments ``(x, y, dx, dy)`` covering a grid from its border to its centre."""
    left, right = 0, columns - 1
    top, bottom = 0, rows - 1
    segments = []
    while left <= right and top <= bottom:
        segments.append((left, top, right - left, 0))
        top += 1
        if top <= bottom:
            segments.append((right, top, 0, bottom - top))
            right -= 1
        if left <= right and top <= bottom:
            segments.append((right, bottom, left - right, 0))
            bottom -= 1
        if top <= bottom and left <= right:
            segments.append((left, bottom, 0, top - bottom))
            left += 1
    return segments


class LevelsScene(Scene):
    """World map: walk with the arrows, confirm on a level tile to enter it.

    A tile named ``levelN`` opens the scene ``level_N`` if there is one,
    otherwise the map ``res/maps/level_N.json`` made with the map editor.
    Levels without either show a message instead of crashing the game.
    """

    # Can be changed in the "worldMap" section of res/rules.yaml.
    ENTER_DURATION = 1.0
    MESSAGE_DURATION = 2.0
    STEP_DURATION = 0.1  # seconds to walk from a tile to the next one
    MUSIC = "world_map"

    def __init__(self, context: GameContext, map_name: str = "levels"):
        super().__init__(context)
        tune(self, context.rules.world_map, "rules.yaml: worldMap")
        self.map_name = map_name
        self.player = Player((), (0, 0), context.sprites.animation("world_mario", "on_map"))
        self.walker: Optional[WorldMapWalker] = None
        self.world = None

    def on_enter(self) -> None:
        super().on_enter()
        world = self.context.maps.change_map(self.map_name)
        if world is not self.world:
            start = world.find("start")
            if start is None:
                raise ValueError(f"Map {self.map_name!r} needs a tile named 'start'")
            self.world = world
            # Kept between visits: coming back from a level leaves Mario where he was.
            self.walker = WorldMapWalker(start.cell, world.is_blocked, self.STEP_DURATION)
            self.levels = Surface((world.width, world.height))

        width, height = self.surface.get_size()
        hud = self.context.hud
        self.levels_pos = Vector2(0, height // 2 - world.height // 2)
        self.hud_pos = Vector2(width // 2 - hud.get_width() // 2, height - hud.get_height())
        hud.refresh(self.context.save)

        self.state: Optional[AnimationState] = None
        self.held: List[Action] = []
        self.spiral: List[Segment] = []
        self.spiral_index = 0
        self.target_scene: Optional[str] = None
        self.target_level = None
        self.message: Optional[Surface] = None
        self.message_timer = 0.0
        self.player.play(self.player.levels_animation)
        self.player.vector = self.walker.position
        self.context.audio.play_music(self.MUSIC)

    def walk(self, direction: Action) -> None:
        if self.walker.try_move(direction):
            self.context.audio.play("map_move")

    def level_under_player(self) -> Tuple[Optional[Tile], Optional[str]]:
        if self.walker.moving:
            return None, None
        tile = self.world.tile_at(*self.walker.cell)
        return tile, level_scene_of(tile.id) if tile is not None else None

    def enter_level(self) -> None:
        tile, scene = self.level_under_player()
        if scene is None:
            return
        number = scene.rsplit("_", 1)[-1]
        if self.manager.has_scene(scene):
            self.target_scene = scene
        else:
            levels = self.context.levels
            level = levels.find(scene) if levels is not None else None
            if level is None:
                self.show_message(f"LEVEL {number} COMING SOON")
                return
            if not level.playable:
                self.show_message(f"LEVEL {number} CANNOT BE PLAYED")
                return
            self.target_level = level
        self.spiral = inverse_spiral_segments(self.world.columns, self.world.rows)
        self.state = AnimationState.ENTER_WORLD
        self.timer = 0.0
        self.context.audio.stop_music()
        self.context.audio.play("enter_level")

    def show_message(self, text: str) -> None:
        self.message = self.context.font.render(text)
        self.message_timer = self.MESSAGE_DURATION

    def on_action(self, action: Action) -> None:
        if self.state is not None:
            return
        if action in DIRECTIONS:
            self.held.append(action)
            self.walk(action)
        elif action == Action.CONFIRM:
            self.enter_level()
        elif action == Action.BACK:
            self.manager.change_scene("main_menu")

    def on_action_released(self, action: Action) -> None:
        while action in self.held:
            self.held.remove(action)

    def update(self, dt: float) -> None:
        super().update(dt)
        self.message_timer = max(0.0, self.message_timer - dt)
        if self.state is None:
            self.world.update(dt)
            was_moving = self.walker.moving
            self.walker.update(dt)
            if was_moving and not self.walker.moving and self.level_under_player()[1]:
                # Like in SMB3, walking stops on each level: press again to go on.
                self.held.clear()
            if not self.walker.moving and self.held:
                self.walk(self.held[-1])
            self.player.vector = self.walker.position
            self.player.update(dt)
        elif self.state == AnimationState.ENTER_WORLD:
            t = min(self.timer / self.ENTER_DURATION, 1.0)
            self.spiral_index = round(len(self.spiral) * t)
            if t >= 1.0:
                if self.target_level is not None:
                    self.context.play_level(
                        self.target_level, lambda cleared: self.manager.change_scene("levels")
                    )
                else:
                    self.manager.change_scene(self.target_scene)

    def draw(self) -> None:
        self.surface.fill(BLACK)
        self.world.draw(self.levels)
        self.levels.blit(self.player.image, self.player.rect)
        for x, y, dx, dy in self.spiral[: self.spiral_index]:
            rect = Rect(
                min(x, x + dx) * Tile.WIDTH,
                min(y, y + dy) * Tile.HEIGHT,
                (abs(dx) + 1) * Tile.WIDTH,
                (abs(dy) + 1) * Tile.HEIGHT,
            )
            pygame.draw.rect(self.levels, BLACK, rect)
        self.surface.blit(self.levels, self.levels_pos)
        self.surface.blit(self.context.hud.image, self.hud_pos)

        if self.message is not None and self.message_timer > 0:
            box = self.message.get_rect(center=(self.surface.get_width() // 2, int(self.levels_pos.y) // 2))
            pygame.draw.rect(self.surface, BLACK, box.inflate(8, 8))
            pygame.draw.rect(self.surface, WHITE, box.inflate(8, 8), 1)
            self.surface.blit(self.message, box)
