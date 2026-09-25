from __future__ import annotations

import math
from enum import Enum, auto
from itertools import combinations
from typing import Callable, Dict, List, Optional, Set, Tuple

import pygame
from pygame import Rect, Surface, transform

from ..constants import BLACK, TILE_HEIGHT, TILE_WIDTH, WHITE
from ..entities.entity import Entity, Sprites
from ..entities.mushroom import Mushroom
from ..entities.spawner import spawn_entities
from ..inputs.config import Action
from ..inputs.map import Map
from ..inputs.save import Game, PlayerState
from ..levels import LevelInfo
from ..platformer import Body, Controls
from ..tile import Tile
from .scene import GameContext, Scene

SKY = (160, 220, 252)
FinishCallback = Callable[[bool], None]
Cell = Tuple[int, int]


class State(Enum):
    ERROR = auto()
    PLAYING = auto()
    PAUSED = auto()
    DYING = auto()
    CLEAR = auto()
    GAME_OVER = auto()


class MarioSprites:
    """Frames of small and big Mario; the sheet draws him facing left."""

    def __init__(self, sheet: Surface):
        def frame(x: int, y: int, height: int = TILE_HEIGHT) -> Dict[int, Surface]:
            left = sheet.subsurface((x, y), (TILE_WIDTH, height))
            return {-1: left, 1: transform.flip(left, True, False)}

        self.small = {
            "stand": frame(0, 0),
            "walk": [frame(0, 0), frame(16, 0)],
            "run": [frame(16, 0), frame(32, 0)],
            "skid": frame(48, 0),
            "jump": frame(0, 64),
        }
        self.big = {
            "stand": frame(0, 80, 28),
            "walk": [frame(0, 80, 28), frame(16, 80, 28)],
            "run": [frame(0, 137, 27), frame(16, 137, 27)],
            "skid": frame(0, 109, 27),
            "jump": frame(32, 80, 28),
        }
        self.dead = frame(16, 16)[1]

    def image_of(self, body: Body, time: float, big: bool = False) -> Surface:
        frames = self.big if big else self.small
        facing = body.facing
        if body.jumping:
            return frames["jump"][facing]
        if body.skidding:
            return frames["skid"][facing]
        speed = abs(body.vx)
        if speed < 1:
            return frames["stand"][facing]
        running = speed > Body.WALK_SPEED + 5
        steps = frames["run"] if running else frames["walk"]
        period = 0.06 if running else 0.12
        return steps[int(time / period) % len(steps)][facing]


class PlatformLevelScene(Scene):
    """A map of ``res/maps`` played as a platform level.

    Solid cells are the collisions painted in the map editor. Coins are
    collected, ``?`` blocks give a coin (or the item hidden in them) when hit
    from below, big Mario breaks bricks, and the entities placed with the
    editor come to life when Mario gets close. Reaching the right edge of the
    map clears the course and falling out of it loses a life.

    The scene is the :class:`~src.entities.entity.Level` of its entities.
    """

    NAME = "platform_level"
    TIME_LIMIT = 300
    COIN_SCORE = 50
    BLOCK_SCORE = 100
    BRICK_SCORE = 10
    MUSHROOM_SCORE = 1000
    # A stomp chain (without touching the ground) scores more and more.
    STOMP_SCORES = (100, 200, 400, 800, 1000, 2000, 4000, 8000)
    STOMP_BOUNCE = 200.0
    STOMP_BOUNCE_HELD = 320.0  # the jump key held
    STOMP_TOLERANCE = 4  # pixels of Mario's feet under the head still stomping
    STOMP_IGNORE = 0.2
    TIME_BONUS = 50
    COINS_PER_LIFE = 100
    DEATH_PAUSE = 0.5
    DEATH_DURATION = 3.0
    CLEAR_DELAY = 1.5
    TIME_COUNT_SPEED = 150  # time units turned into score per second
    BUMP_DURATION = 0.15
    COIN_POP_DURATION = 0.45
    POPUP_DURATION = 0.8
    # Growing or shrinking pauses the level; then Mario blinks and cannot be hurt.
    TRANSITION_DURATION = 0.6
    INVINCIBLE_DURATION = 1.5
    # Entities wake up this far outside the view.
    ACTIVATION_MARGIN = 2 * TILE_WIDTH

    def __init__(self, context: GameContext):
        super().__init__(context)
        self.sprites = MarioSprites(context.ressources.image("mario"))
        self.entity_sprites = Sprites(context.ressources)
        self.level: Optional[LevelInfo] = None
        self.on_finish: FinishCallback = lambda cleared: None
        self.practice = False
        self.map: Optional[Map] = None
        self.error: Optional[str] = None
        self.state = State.ERROR
        self.finished = False
        self.start_big = False

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
        self.start_big = self.context.save.game.state is PlayerState.BIG
        self.restart()

    def restart(self) -> None:
        """(Re)loads the map: collected coins and defeated enemies come back."""
        self.timer = 0.0
        self.clock = 0.0
        self.state_timer = 0.0
        self.jump_pressed = False
        self.bumps: Dict[Tile, float] = {}
        self.coin_pops: List[List[float]] = []
        self.popups: List[list] = []
        self.debris: List[list] = []
        self.entities: List[Entity] = []
        self.hidden_items: Dict[Cell, Mushroom] = {}
        self.time_left = float(self.TIME_LIMIT)
        self.message: Optional[str] = None
        self.finished = False
        self.big = False
        self.combo = 0
        self.transition = 0.0
        self.invincible = 0.0
        try:
            if self.level is None:
                raise ValueError("No level to play")
            self.map = self.context.levels.load(self.level)
            self.entities, start = spawn_entities(self.map.entities, self.entity_sprites, self.is_solid)
        except (OSError, ValueError, KeyError) as error:
            self.map = None
            self.error = str(error)
            self.state = State.ERROR
            return
        self.hidden_items = {
            (entity.column, entity.row): entity
            for entity in self.entities
            if isinstance(entity, Mushroom) and entity.hidden
        }
        self.error = None
        self.state = State.PLAYING
        self.body = Body(0, 0)
        self.body.x, self.body.y = self.spawn_point(start)
        if self.start_big:
            self._set_big(True)
        self.camera = pygame.Vector2(0, 0)
        self._move_camera()

    def spawn_point(self, start=None) -> Tuple[float, float]:
        """On the start marker of the map, else on the first ground from the left."""
        def standing_on(column: int, row: int) -> Tuple[float, float]:
            return column * TILE_WIDTH + (TILE_WIDTH - Body.WIDTH) / 2, row * TILE_HEIGHT - Body.HEIGHT

        if start is not None:
            return standing_on(start.column, start.row + 1)
        for column in range(self.map.columns):
            for row in range(1, self.map.rows):
                if self.is_solid(column, row) and not self.is_solid(column, row - 1):
                    return standing_on(column, row)
        return (TILE_WIDTH - Body.WIDTH) / 2, 0

    def is_solid(self, column: int, row: int) -> bool:
        """The sides of the map are walls, its top and bottom are open."""
        if column < 0 or column >= self.map.columns:
            return True
        if row < 0 or row >= self.map.rows:
            return False
        return self.map.collidables[row][column]

    @property
    def mario(self) -> Body:
        return self.body

    @property
    def height(self) -> int:
        return self.map.height

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
        if self.transition > 0:
            self.transition = max(0.0, self.transition - dt)
            return
        body = self.body
        previous_bottom = body.bottom
        for cell in body.update(dt, self.controls(), self.is_solid):
            self.bump(*cell)
        if body.on_ground:
            self.combo = 0
        self.invincible = max(0.0, self.invincible - dt)
        self._collect_coins()
        self._update_entities(dt, previous_bottom)
        if self.state != State.PLAYING:
            return
        self.time_left = max(0.0, self.time_left - dt)
        if body.y > self.map.height + TILE_HEIGHT or self.time_left <= 0:
            self.die()
        elif body.x + body.width >= self.map.width - 0.01:
            self._set_state(State.CLEAR)
            self.message = "COURSE CLEAR"
        self._move_camera()

    def _update_entities(self, dt: float, mario_previous_bottom: float) -> None:
        view_width, _ = self.view_size
        left = self.camera.x - self.ACTIVATION_MARGIN
        right = self.camera.x + view_width + self.ACTIVATION_MARGIN
        for entity in self.entities:
            if not entity.active and left <= entity.body.center_x <= right:
                entity.activate(self)
        for entity in self.entities:
            if entity.active and not entity.removed:
                entity.update(dt, self)
        self._collide_entities()
        self._touch_mario(mario_previous_bottom)
        self.entities = [entity for entity in self.entities if not entity.removed]

    def _collide_entities(self) -> None:
        """Kicked shells knock enemies out, other enemies turn back when they meet."""
        enemies = [entity for entity in self.entities if entity.ENEMY and entity.alive]
        for first, second in combinations(enemies, 2):
            if not (first.alive and second.alive) or not first.rect.colliderect(second.rect):
                continue
            first_shell = getattr(first, "kills_enemies", False)
            second_shell = getattr(second, "kills_enemies", False)
            if first_shell:
                second.knock(self, first.direction)
            if second_shell:
                first.knock(self, second.direction)
            if first_shell or second_shell:
                continue
            left, right = sorted((first, second), key=lambda entity: entity.body.center_x)
            if left.direction > 0:
                left.turn_around()
            if right.direction < 0:
                right.turn_around()

    def _touch_mario(self, previous_bottom: float) -> None:
        mario = self.body.rect
        for entity in list(self.entities):
            if self.state != State.PLAYING or self.transition > 0:
                return
            if not entity.alive or entity.ignore_mario > 0 or not mario.colliderect(entity.rect):
                continue
            stomp = (
                entity.ENEMY
                and self.body.vy > 0
                and previous_bottom <= entity.rect.top + self.STOMP_TOLERANCE
            )
            entity.touch_mario(self, stomp)

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
        self._set_big(False)
        self.start_big = False
        self._set_state(State.DYING)
        self.body.vy = -260.0
        self.message = "TIME UP" if self.time_left <= 0 else None

    def _set_state(self, state: State) -> None:
        self.state = state
        self.state_timer = 0.0
        self.held.clear()

    def _set_big(self, big: bool) -> None:
        if big != self.big:
            self.body.resize(Body.BIG_HEIGHT if big else Body.HEIGHT)
        self.big = big
        if not self.practice:
            self.context.save.game.state = PlayerState.BIG if big else PlayerState.LITTLE

    # ------------------------------------------------- the Level of entities

    def hurt_mario(self) -> None:
        if self.state != State.PLAYING or self.invincible > 0 or self.transition > 0:
            return
        if not self.big:
            self.die()
            return
        self._set_big(False)
        self.transition = self.TRANSITION_DURATION
        self.invincible = self.INVINCIBLE_DURATION

    def stomped(self, entity: Entity) -> None:
        entity.ignore_mario = self.STOMP_IGNORE
        self.body.vy = -(self.STOMP_BOUNCE_HELD if Action.CONFIRM in self.held else self.STOMP_BOUNCE)
        self.body.on_ground = False
        x, y = entity.body.center_x, entity.body.y
        if self.combo < len(self.STOMP_SCORES):
            self.score(self.STOMP_SCORES[self.combo], x, y)
        else:
            self.add_life(x, y)
        self.combo += 1

    def score(self, points: int, x: float, y: float) -> None:
        self.context.save.game.score += points
        self.popups.append([str(points), x, y, 0.0])

    def grow_mario(self, x: float, y: float) -> None:
        self.score(self.MUSHROOM_SCORE, x, y)
        if not self.big:
            self._set_big(True)
            self.transition = self.TRANSITION_DURATION

    def add_life(self, x: float, y: float) -> None:
        self.context.save.game.life += 1
        self.popups.append(["1UP", x, y, 0.0])

    # ------------------------------------------------------ coins and blocks

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
        item = self.hidden_items.pop((column, row), None)
        if tile is None and item is None:
            return
        self._knock_entities_on(column, row)
        if tile is not None:
            self.bumps[tile] = self.BUMP_DURATION
        if item is not None:
            item.emerge()
            if tile is not None and self.map.has_tile_named("block"):
                self.map.replace(tile, "block")
        elif tile.id.startswith("mystery_block") and self.map.has_tile_named("block"):
            self.map.replace(tile, "block")
            self.add_coin(self.BLOCK_SCORE)
            self.coin_pops.append([tile.rect.x, tile.rect.y - TILE_HEIGHT, 0.0])
        elif tile.id.startswith("brick") and self.big:
            self._break(tile, column, row)

    def _knock_entities_on(self, column: int, row: int) -> None:
        """What stands on a bumped block is knocked out (enemies) or hops (items)."""
        cell = Rect(column * TILE_WIDTH, row * TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT)
        for entity in self.entities:
            rect = entity.rect
            if entity.alive and abs(rect.bottom - cell.top) <= 2 and cell.left < rect.right and rect.left < cell.right:
                entity.knock(self, 1 if rect.centerx >= cell.centerx else -1)

    def _break(self, tile: Tile, column: int, row: int) -> None:
        self.bumps.pop(tile, None)
        image = tile.image
        self.map.remove(tile)
        self.map.set_collidable(column, row, False)
        self.context.save.game.score += self.BRICK_SCORE
        half_width, half_height = TILE_WIDTH // 2, TILE_HEIGHT // 2
        for dx in (0, 1):
            for dy in (0, 1):
                piece = image.subsurface((dx * half_width, dy * half_height, half_width, half_height)).copy()
                self.debris.append([
                    piece,
                    column * TILE_WIDTH + dx * half_width,
                    row * TILE_HEIGHT + dy * half_height,
                    (dx * 2 - 1) * 60.0,
                    -300.0 + dy * 100.0,
                ])

    def _update_effects(self, dt: float) -> None:
        for tile in list(self.bumps):
            self.bumps[tile] -= dt
            if self.bumps[tile] <= 0:
                del self.bumps[tile]
        for pop in self.coin_pops:
            pop[2] += dt
        self.coin_pops = [pop for pop in self.coin_pops if pop[2] < self.COIN_POP_DURATION]
        for popup in self.popups:
            popup[3] += dt
        self.popups = [popup for popup in self.popups if popup[3] < self.POPUP_DURATION]
        for piece in self.debris:
            piece[4] = min(piece[4] + Body.GRAVITY * dt, Body.MAX_FALL_SPEED * 2)
            piece[1] += piece[3] * dt
            piece[2] += piece[4] * dt
        self.debris = [piece for piece in self.debris if piece[2] < self.map.height + TILE_HEIGHT]

    def _move_camera(self) -> None:
        view_width, view_height = self.view_size
        body = self.body

        def clamp(value, size, view):
            if size <= view:
                return (size - view) / 2  # smaller than the screen: centred
            return max(0, min(value, size - view))

        self.camera.x = clamp(body.center_x - view_width / 2, self.map.width, view_width)
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
        self._draw_entities(behind_tiles=True)
        self._draw_tiles(view)
        self._draw_coin_pops()
        self._draw_entities(behind_tiles=False)
        self._draw_mario()
        self._draw_debris()
        self._draw_popups()
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

    def _draw_entities(self, behind_tiles: bool) -> None:
        for entity in self.entities:
            if entity.active and entity.behind_tiles == behind_tiles:
                entity.draw(self.surface, self.camera.x, self.camera.y)

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
            big = self.big
            if self.transition > 0:
                # Blinks between his two sizes while growing or shrinking.
                big = int(self.transition / 0.08) % 2 == (0 if self.big else 1)
            elif self.invincible > 0 and int(self.invincible / 0.05) % 2:
                return
            image = self.sprites.image_of(body, self.clock, big)
        x = body.center_x - image.get_width() / 2 - self.camera.x
        y = body.bottom - image.get_height() - self.camera.y
        self.surface.blit(image, (round(x), round(y)))

    def _draw_debris(self) -> None:
        for image, x, y, _, _ in self.debris:
            self.surface.blit(image, (round(x - self.camera.x), round(y - self.camera.y)))

    def _draw_popups(self) -> None:
        font = self.context.font
        for text, x, y, age in self.popups:
            image = font.render(text)
            rise = 24 * age / self.POPUP_DURATION
            self.surface.blit(
                image,
                (round(x - image.get_width() / 2 - self.camera.x), round(y - 8 - rise - self.camera.y)),
            )

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
