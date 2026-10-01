"""Transient visual effects for a platform level, separate from gameplay state."""

from __future__ import annotations

import math
from typing import Dict, List

from pygame import Surface, Vector2

from ..constants import TILE_HEIGHT, TILE_WIDTH
from ..inputs.map import Map
from ..tile import Tile


class LevelEffects:
    def __init__(self, bump_duration: float, coin_duration: float, popup_duration: float):
        self.bump_duration = bump_duration
        self.coin_duration = coin_duration
        self.popup_duration = popup_duration
        self.bumps: Dict[Tile, float] = {}
        self.coin_pops: List[List[float]] = []
        self.popups: List[list] = []
        self.debris: List[list] = []

    def break_tile(self, tile: Tile, column: int, row: int) -> None:
        self.bumps.pop(tile, None)
        half_width, half_height = TILE_WIDTH // 2, TILE_HEIGHT // 2
        for dx in (0, 1):
            for dy in (0, 1):
                piece = tile.image.subsurface(
                    (dx * half_width, dy * half_height, half_width, half_height)
                ).copy()
                self.debris.append([
                    piece,
                    column * TILE_WIDTH + dx * half_width,
                    row * TILE_HEIGHT + dy * half_height,
                    (dx * 2 - 1) * 60.0,
                    -300.0 + dy * 100.0,
                ])

    def update(self, dt: float, gravity: float, max_fall_speed: float, map_height: int) -> None:
        for tile in list(self.bumps):
            self.bumps[tile] -= dt
            if self.bumps[tile] <= 0:
                del self.bumps[tile]
        for pop in self.coin_pops:
            pop[2] += dt
        self.coin_pops = [pop for pop in self.coin_pops if pop[2] < self.coin_duration]
        for popup in self.popups:
            popup[3] += dt
        self.popups = [popup for popup in self.popups if popup[3] < self.popup_duration]
        for piece in self.debris:
            piece[4] = min(piece[4] + gravity * dt, max_fall_speed * 2)
            piece[1] += piece[3] * dt
            piece[2] += piece[4] * dt
        self.debris = [piece for piece in self.debris if piece[2] < map_height + TILE_HEIGHT]

    def tile_offset(self, tile: Tile) -> int:
        if tile not in self.bumps:
            return 0
        return -round(4 * math.sin(math.pi * (1 - self.bumps[tile] / self.bump_duration)))

    def draw_coins(self, surface: Surface, camera: Vector2, level_map: Map) -> None:
        coins = level_map.names_with("coin")
        if not self.coin_pops or not coins:
            return
        coin = level_map.image_of(coins[0])
        for x, y, age in self.coin_pops:
            height = 24 * math.sin(math.pi * age / self.coin_duration)
            surface.blit(coin, (x - round(camera.x), y - height - round(camera.y)))

    def draw_debris(self, surface: Surface, camera: Vector2) -> None:
        for image, x, y, _, _ in self.debris:
            surface.blit(image, (round(x - camera.x), round(y - camera.y)))

    def draw_popups(self, surface: Surface, camera: Vector2, font) -> None:
        for text, x, y, age in self.popups:
            image = font.render(text)
            rise = 24 * age / self.popup_duration
            surface.blit(
                image,
                (round(x - image.get_width() / 2 - camera.x), round(y - 8 - rise - camera.y)),
            )
