import pygame

from ..tile import Tile
from ..camera import Camera
from ..entities.player import Player
from ..hud import HUD
from ..map_manager import MapManager
from .scene import Scene


class Level1Scene(Scene):
    def __init__(self):
        super().__init__()
        self.map_manager = MapManager()

        self.hud = HUD()
        self.hud_pos = pygame.Vector2(
            self.surface.get_width() / 2 - self.hud.get_width() / 2,
            self.surface.get_height() - self.hud.get_height(),
        )

    def on_enter(self):
        self.map_manager.change_map("level_1")
        self.level = pygame.Surface(
            (self.map_manager.current.width, self.map_manager.current.height)
        )
        self.level_pos = pygame.Vector2(0, 0)

        self.player = Player(
            self.map_manager.current.sprites, pygame.Vector2(0, 0)
        )
        self.camera = Camera(
            self.player.vector.x,
            self.player.vector.y,
            Tile.WIDTH * 29,
            Tile.HEIGHT * 15,
            self.level.get_width(),
            self.level.get_height()
        )

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z:
                self.player.vector.y = self.player.vector.y - 16
            if event.key == pygame.K_q:
                self.player.vector.x = self.player.vector.x - 16
            if event.key == pygame.K_s:
                self.player.vector.y = self.player.vector.y + 16
            if event.key == pygame.K_d:
                self.player.vector.x = self.player.vector.x + 16

    def update(self, dt):
        self.map_manager.update(dt)
        self.camera.update(self.player.vector.x, self.player.vector.y)
        
        if any(
            self.player.rect.colliderect(tile.rect) and tile.collidable
            for tile in self.map_manager.current.sprites
            if tile != self.player
        ):
            pass

    def draw(self):
        self.surface.fill((0, 0, 0))
        self.level.fill((181, 235, 242))

        self.map_manager.draw(self.level)
        level_cam = self.level.subsurface(self.camera)
        level_cam.blit(self.hud, self.hud_pos)
        self.surface.blit(level_cam, self.level_pos)
