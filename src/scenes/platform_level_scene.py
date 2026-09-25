from __future__ import annotations

import math
from enum import Enum, auto
from typing import Callable, Dict, List, Optional, Set

import pygame
from pygame import Rect, Surface, transform

from ..constants import BLACK, TILE_HEIGHT, TILE_WIDTH, WHITE
from ..inputs.config import Action
from ..inputs.map import Map
from ..inputs.save import Game
from ..levels import LevelInfo
from ..platformer import Body, Controls
from ..tile import Tile
from .scene import GameContext, Scene

SKY = (160, 220, 252)
FinishCallback = Callable[[bool], None]


class State(Enum):
    ERROR = auto()
    PLAYING = auto()
    PAUSED = auto()
    DYING = auto()
    CLEAR = auto()
    GAME_OVER = auto()


class MarioSprites:
    """Frames of small Mario; the sheet draws him facing left."""

    def __init__(self, sheet: Surface):
        def frame(x: int, y: int) -> Dict[int, Surface]:
            left = sheet.subsurface((x, y), (TILE_WIDTH, TILE_HEIGHT))
            return {-1: left, 1: transform.flip(left, True, False)}

        self.stand = frame(0, 0)
        self.walk = [frame(0, 0), frame(16, 0)]
        self.run = [frame(16, 0), frame(32, 0)]
        self.skid = frame(48, 0)
        self.jump = frame(0, 64)
        self.dead = frame(16, 16)[1]

    def image_of(self, body: Body, time: float) -> Surface:
        facing = body.facing
        if body.jumping:
            return self.jump[facing]
        if body.skidding:
            return self.skid[facing]
        speed = abs(body.vx)
        if speed < 1:
            return self.stand[facing]
        frames = self.run if speed > Body.WALK_SPEED + 5 else self.walk
        period = 0.06 if frames is self.run else 0.12
        return frames[int(time / period) % len(frames)][facing]


class PlatformLevelScene(Scene):
    """A map of ``res/maps`` played as a platform level.

    Solid cells are the collisions painted in the map editor. Coins are
    collected, ``?`` blocks give a coin when hit from below, reaching the right
    edge of the map clears the course and falling out of it loses a life.
    """

    NAME = "platform_level"
    TIME_LIMIT = 300
    COIN_SCORE = 50
    BLOCK_SCORE = 100
    TIME_BONUS = 50
    COINS_PER_LIFE = 100
    DEATH_PAUSE = 0.5
    DEATH_DURATION = 3.0
    CLEAR_DELAY = 1.5
    TIME_COUNT_SPEED = 150  # time units turned into score per second
    BUMP_DURATION = 0.15
    COIN_POP_DURATION = 0.45

    def __init__(self, context: GameContext):
        super().__init__(context)
        self.sprites = MarioSprites(context.ressources.image("mario"))
        self.level: Optional[LevelInfo] = None
        self.on_finish: FinishCallback = lambda cleared: None
        self.practice = False
        self.map: Optional[Map] = None
        self.error: Optional[str] = None
        self.state = State.ERROR
        self.finished = False

    def start(self, level: LevelInfo, on_finish: FinishCallback, practice: bool = False) -> None:
        """Plays ``level``; ``on_finish(cleared)`` is called when it is left.

        In practice mode (testing from the editor) no life is lost.
        """
        self.level = level
        self.on_finish = on_finish
        self.practice = practice
        self.manager.change_scene(self.NAME)

    # ------------------------------------------------------------------ state

    def on_enter(self) -> None:
        super().on_enter()
        self.held: Set[Action] = set()
        self.restart()

    def restart(self) -> None:
        """(Re)loads the map: collected coins come back."""
        self.timer = 0.0
        self.clock = 0.0
        self.state_timer = 0.0
        self.jump_pressed = False
        self.bumps: Dict[Tile, float] = {}
        self.coin_pops: List[List[float]] = []
        self.time_left = float(self.TIME_LIMIT)
        self.message: Optional[str] = None
        self.finished = False
        try:
            if self.level is None:
                raise ValueError("No level to play")
            self.map = self.context.levels.load(self.level)
        except (OSError, ValueError, KeyError) as error:
            self.map = None
            self.error = str(error)
            self.state = State.ERROR
            return
        self.error = None
        self.state = State.PLAYING
        self.body = Body(*self.spawn_point())
        self.camera = pygame.Vector2(0, 0)
        self._move_camera()

    def spawn_point(self):
        """On the first ground from the left of the map."""
        for column in range(self.map.columns):
            for row in range(1, self.map.rows):
                if self.is_solid(column, row) and not self.is_solid(column, row - 1):
                    x = column * TILE_WIDTH + (TILE_WIDTH - Body.WIDTH) / 2
                    return x, row * TILE_HEIGHT - Body.HEIGHT
        return (TILE_WIDTH - Body.WIDTH) / 2, 0

    def is_solid(self, column: int, row: int) -> bool:
        """The sides of the map are walls, its top and bottom are open."""
        if column < 0 or column >= self.map.columns:
            return True
        if row < 0 or row >= self.map.rows:
            return False
        return self.map.collidables[row][column]

    @property
    def view_size(self):
        width, height = self.surface.get_size()
        return width, height - self.context.hud.get_height()

    def finish(self, cleared: bool) -> None:
        # The level is left once, even if on_finish does not change the scene.
        if self.finished:
            return
        self.finished = True
        self.on_finish(cleared)

    # ------------------------------------------------------------------ input

    def on_action(self, action: Action) -> None:
        if self.finished:
            return
        if self.state == State.ERROR:
            if action in (Action.CONFIRM, Action.BACK):
                self.finish(False)
            return
        if self.state == State.PAUSED:
            if action == Action.CONFIRM:
                self.state = State.PLAYING
            elif action == Action.BACK:
                self.finish(False)
            return
        self.held.add(action)
        if action == Action.CONFIRM:
            self.jump_pressed = True
        elif action == Action.BACK and self.state == State.PLAYING:
            self.state = State.PAUSED
            self.held.clear()

    def on_action_released(self, action: Action) -> None:
        self.held.discard(action)

    def controls(self) -> Controls:
        held = self.held
        controls = Controls(
            left=Action.LEFT in held,
            right=Action.RIGHT in held,
            run=Action.RUN in held,
            jump=Action.CONFIRM in held,
            jump_pressed=self.jump_pressed,
        )
        self.jump_pressed = False
        return controls

    # ----------------------------------------------------------------- update

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.finished or self.state in (State.ERROR, State.PAUSED):
            return
        self.clock += dt
        self.state_timer += dt
        self.map.update(dt)
        self._update_effects(dt)
        if self.state == State.PLAYING:
            self._update_playing(dt)
        elif self.state == State.DYING:
            self._update_dying(dt)
        elif self.state == State.CLEAR:
            self._update_clear(dt)
        elif self.state == State.GAME_OVER and self.state_timer >= self.CLEAR_DELAY * 2:
            self.context.save.game = Game(level=self.context.save.game.level)
            self.finish(False)
        self.context.hud.refresh(self.context.save, math.ceil(self.time_left))

    def _update_playing(self, dt: float) -> None:
        body = self.body
        for cell in body.update(dt, self.controls(), self.is_solid):
            self.bump(*cell)
        self._collect_coins()
        self.time_left = max(0.0, self.time_left - dt)
        if body.y > self.map.height + TILE_HEIGHT or self.time_left <= 0:
            self.die()
        elif body.x + Body.WIDTH >= self.map.width - 0.01:
            self._set_state(State.CLEAR)
            self.message = "COURSE CLEAR"
        self._move_camera()

    def _update_dying(self, dt: float) -> None:
        if self.state_timer >= self.DEATH_PAUSE:
            self.body.vy = min(self.body.vy + Body.GRAVITY * 0.7 * dt, Body.MAX_FALL_SPEED)
            self.body.y += self.body.vy * dt
        if self.state_timer < self.DEATH_DURATION:
            return
        game = self.context.save.game
        if self.practice:
            self.restart()
        elif game.life > 1:
            game.life -= 1
            self.restart()
        else:
            game.life = 0
            self._set_state(State.GAME_OVER)
            self.message = "GAME OVER"

    def _update_clear(self, dt: float) -> None:
        if self.time_left > 0:
            units = min(self.time_left, math.ceil(self.TIME_COUNT_SPEED * dt))
            self.time_left -= units
            self.context.save.game.score += int(units) * self.TIME_BONUS
            self.state_timer = 0.0
        elif self.state_timer >= self.CLEAR_DELAY:
            self.finish(True)

    def die(self) -> None:
        self._set_state(State.DYING)
        self.body.vy = -260.0
        self.message = "TIME UP" if self.time_left <= 0 else None

    def _set_state(self, state: State) -> None:
        self.state = state
        self.state_timer = 0.0
        self.held.clear()

    def _collect_coins(self) -> None:
        rect = self.body.rect
        for column in range(rect.left // TILE_WIDTH, (rect.right - 1) // TILE_WIDTH + 1):
            for row in range(rect.top // TILE_HEIGHT, (rect.bottom - 1) // TILE_HEIGHT + 1):
                tile = self.map.tile_at(column, row)
                if tile is not None and tile.id.startswith("coin") and rect.colliderect(tile.rect):
                    self.map.remove(tile)
                    self.add_coin(self.COIN_SCORE)

    def add_coin(self, score: int) -> None:
        game = self.context.save.game
        game.score += score
        game.coins += 1
        if game.coins >= self.COINS_PER_LIFE:
            game.coins -= self.COINS_PER_LIFE
            game.life += 1

    def bump(self, column: int, row: int) -> None:
        """Mario's head hit a solid cell from below."""
        tile = self.map.tile_at(column, row)
        if tile is None:
            return
        self.bumps[tile] = self.BUMP_DURATION
        if tile.id.startswith("mystery_block") and self.map.has_tile_named("block"):
            self.map.replace(tile, "block")
            self.add_coin(self.BLOCK_SCORE)
            self.coin_pops.append([tile.rect.x, tile.rect.y - TILE_HEIGHT, 0.0])

    def _update_effects(self, dt: float) -> None:
        for tile in list(self.bumps):
            self.bumps[tile] -= dt
            if self.bumps[tile] <= 0:
                del self.bumps[tile]
        for pop in self.coin_pops:
            pop[2] += dt
        self.coin_pops = [pop for pop in self.coin_pops if pop[2] < self.COIN_POP_DURATION]

    def _move_camera(self) -> None:
        view_width, view_height = self.view_size
        body = self.body

        def clamp(value, size, view):
            if size <= view:
                return (size - view) / 2  # smaller than the screen: centred
            return max(0, min(value, size - view))

        self.camera.x = clamp(body.x + Body.WIDTH / 2 - view_width / 2, self.map.width, view_width)
        # The view stays on the ground and only goes up when Mario climbs high.
        self.camera.y = clamp(
            min(self.map.height - view_height, body.y - view_height / 3), self.map.height, view_height
        )

    # ------------------------------------------------------------------- draw

    def draw(self) -> None:
        surface = self.surface
        surface.fill(BLACK)
        if self.state == State.ERROR:
            self._draw_lines(["THIS LEVEL CANNOT BE PLAYED", "", *self.context.font.wrap(self.error or "", 54),
                              "", "PRESS A TO GO BACK"], surface.get_height() // 2)
            return

        view_width, view_height = self.view_size
        view = Rect(0, 0, view_width, view_height)
        surface.set_clip(view)
        surface.fill(SKY, Rect(-self.camera.x, -self.camera.y, self.map.width, self.map.height).clip(view))
        self._draw_tiles(view)
        self._draw_coin_pops()
        self._draw_mario()
        surface.set_clip(None)

        hud = self.context.hud
        surface.blit(hud.image, (view_width // 2 - hud.get_width() // 2, view_height))
        if self.state == State.PAUSED:
            self._draw_lines(["PAUSE", "", "PRESS A TO CONTINUE", "PRESS ESC TO QUIT"], view_height // 2)
        elif self.message:
            self._draw_lines([self.message], view_height // 3)

    def _draw_tiles(self, view: Rect) -> None:
        camera_x, camera_y = self.camera
        first_column = max(0, int(camera_x // TILE_WIDTH))
        last_column = min(self.map.columns, int((camera_x + view.width) // TILE_WIDTH) + 1)
        first_row = max(0, int(camera_y // TILE_HEIGHT))
        last_row = min(self.map.rows, int((camera_y + view.height) // TILE_HEIGHT) + 1)
        for row in range(first_row, last_row):
            for column in range(first_column, last_column):
                tile = self.map.tile_at(column, row)
                if tile is None:
                    continue
                offset = 0
                if tile in self.bumps:
                    offset = -round(4 * math.sin(math.pi * (1 - self.bumps[tile] / self.BUMP_DURATION)))
                self.surface.blit(
                    tile.image,
                    (column * TILE_WIDTH - round(camera_x), row * TILE_HEIGHT - round(camera_y) + offset),
                )

    def _draw_coin_pops(self) -> None:
        if not self.coin_pops or not self.map.has_tile_named("coin_frame_0"):
            return
        coin = self.map.image_of("coin_frame_0")
        for x, y, age in self.coin_pops:
            t = age / self.COIN_POP_DURATION
            height = 24 * math.sin(math.pi * t)
            self.surface.blit(coin, (x - round(self.camera.x), y - height - round(self.camera.y)))

    def _draw_mario(self) -> None:
        body = self.body
        if self.state in (State.DYING, State.GAME_OVER):
            image = self.sprites.dead
        else:
            image = self.sprites.image_of(body, self.clock)
        x = body.x + Body.WIDTH / 2 - TILE_WIDTH / 2 - self.camera.x
        y = body.y + Body.HEIGHT - TILE_HEIGHT - self.camera.y
        self.surface.blit(image, (round(x), round(y)))
    def _draw_lines(self, lines: List[str], center_y: int) -> None:
        font = self.context.font
        rendered = [font.render(line) for line in lines]
        height = len(rendered) * 12
        width = max(image.get_width() for image in rendered)
        box = Rect(0, 0, width + 16, height + 8)
        box.center = (self.surface.get_width() // 2, center_y)
        pygame.draw.rect(self.surface, BLACK, box)
        pygame.draw.rect(self.surface, WHITE, box, 1)
        for index, image in enumerate(rendered):
            self.surface.blit(image, (box.centerx - image.get_width() // 2, box.top + 6 + index * 12))
