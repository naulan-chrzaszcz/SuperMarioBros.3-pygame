import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from src.constants import PROJECT_ROOT
from src.editor_bridge import EditorResult, EditorSession
from src.entities.catalog import entity_types
from src.entities.koopa import Koopa, Shell
from src.entities.spawner import known_types
from src.font import Font
from src.game import Game, fit
from src.inputs.config import Action, Config
from src.inputs.map import EntitySpawn, Map, TileCode
from src.inputs.ressources import Ressources
from src.inputs.save import PlayerState, Save
from src.levels import LevelCatalog
from src.platformer import Body, Controls
from src.scene_manager import SceneManager
from src.scenes.levels_scene import inverse_spiral_segments
from src.world_map import WorldMapWalker, level_scene_of

Event = pygame.event.Event


def key_event(key, released=False):
    return Event(pygame.KEYUP if released else pygame.KEYDOWN, key=key, mod=0, unicode="", scancode=0)


def setUpModule():
    pygame.init()
    pygame.display.set_mode((1, 1))


class TileCodeTest(unittest.TestCase):
    def test_codes_written_by_the_map_editor(self):
        self.assertEqual(TileCode.parse("3,4"), TileCode(3, 4))
        self.assertEqual(TileCode.parse("0+4,2"), TileCode(0, 2, x_frames=4))
        self.assertEqual(TileCode.parse("2,5+3&1"), TileCode(2, 5, y_frames=3, rotation=1))
        self.assertEqual(TileCode.parse("0,0&3"), TileCode(0, 0, rotation=3))
        self.assertIsNone(TileCode.parse("-1,-1"))

    def test_invalid_codes(self):
        for code in ("", "1", "a,b", "1+2,3+4", "-2,0", "1+0,1"):
            with self.subTest(code=code), self.assertRaises(ValueError):
                TileCode.parse(code)


class MapTest(unittest.TestCase):
    sheet = pygame.Surface((32, 32))
    names = {"0,0": "grass", "1,0": "start", "0,1": "level1"}

    def make(self, tiles, collidables=None):
        if collidables is None:
            collidables = [[False] * len(row) for row in tiles]
        return Map(self.sheet, self.names, {"tiles": tiles, "collidables": collidables})

    def test_queries(self):
        world = self.make([["1,0", "0,0", "0,1"], ["0,0", "-1,-1", "0,0"]],
                          [[False, True, False], [False] * 3])
        self.assertEqual((world.columns, world.rows, world.width, world.height), (3, 2, 48, 32))
        self.assertEqual(world.find("start").cell, (0, 0))
        self.assertEqual(len(world.tiles_named("grass")), 3)
        self.assertEqual(world.tile_at(2, 0).id, "level1")
        self.assertIsNone(world.tile_at(1, 1))
        self.assertTrue(world.is_blocked(1, 0))
        self.assertTrue(world.is_blocked(-1, 0))
        self.assertTrue(world.is_blocked(0, 2))
        self.assertFalse(world.is_blocked(0, 1))

    def test_errors_are_explicit(self):
        with self.assertRaisesRegex(ValueError, "same number"):
            self.make([["0,0"], []], [[False], []])
        with self.assertRaisesRegex(ValueError, "collision grid"):
            self.make([["0,0"]], [])
        with self.assertRaisesRegex(ValueError, "not declared"):
            self.make([["1,1"]])
        with self.assertRaisesRegex(ValueError, "outside the tileset"):
            self.make([["0+3,0"]])

    def test_animated_tiles_cycle(self):
        world = self.make([["0+2,0"]])
        tile = world.find("grass")
        first = tile.image
        world.update(1 / Map.ANIMATION_SPEED)
        self.assertIsNot(tile.image, first)

    def test_world_map_of_the_game(self):
        world = Ressources.load().load_map("levels")
        self.assertIsNotNone(world.find("start"))
        for number in range(1, 7):
            self.assertIsNotNone(world.find(f"level{number}"))


class ConfigTest(unittest.TestCase):
    def test_missing_file_gives_defaults(self):
        self.assertEqual(Config.load(Path("does-not-exist.yaml")), Config())

    def test_project_config_is_valid(self):
        config = Config.load()
        self.assertEqual((config.display.width, config.display.height), (464, 240))

    def test_sections_and_controls(self):
        config = Config.from_dict(
            {"skipIntro": True, "screen": {"integerScaling": True}, "controls": {"confirm": "x"}}
        )
        self.assertTrue(config.skip_intro)
        self.assertTrue(config.screen.integer_scaling)
        self.assertEqual(config.screen.width, 1280)
        self.assertEqual(config.controls.action_of("x"), Action.CONFIRM)
        self.assertIsNone(config.controls.action_of("a"))
        self.assertEqual(config.controls.action_of("Up"), Action.UP)

    def test_written_settings_are_read_back(self):
        config = Config.from_dict(
            {"skipIntro": True, "audio": {"musicVolume": 0.2}, "controls": {"confirm": "x"}}
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.yaml"
            config.write(path)
            self.assertEqual(Config.load(path), config)

    def test_unknown_settings_are_reported(self):
        for data in ({"skipIntr": True}, {"screen": {"widht": 3}},
                     {"display": {"width": 0}}, {"controls": {"jump": "x"}}):
            with self.subTest(data=data), self.assertRaises(ValueError):
                Config.from_dict(data)


class SaveTest(unittest.TestCase):
    def test_round_trip(self):
        save = Save.from_dict({"game": {"level": "WORLD 3", "score": 12, "inventory": ["mushroom"]}})
        self.assertEqual(save.game.world, "3")
        self.assertEqual(save.game.inventory, ["mushroom", None, None])
        self.assertEqual(save.game.state, PlayerState.LITTLE)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "save.yaml"
            save.write(path)
            self.assertEqual(Save.load(path), save)

    def test_project_save_and_new_game(self):
        self.assertEqual(Save.load().player, "mario")
        self.assertEqual(Save.load(Path("missing.yaml")), Save())


class FontTest(unittest.TestCase):
    def test_glyphs_follow_the_sheet(self):
        sheet = pygame.Surface((len(Font.CHARSET) * 8, 8))
        for index in range(len(Font.CHARSET)):
            sheet.fill((index, 0, 0), ((index * 8, 0), (8, 8)))
        font = Font(sheet)
        # The sheet has no Y: Z comes right after X.
        self.assertEqual(font.render("Z").get_at((0, 0))[0], 24)
        self.assertEqual(font.render("0").get_at((0, 0))[0], 25)
        self.assertEqual(font.render("b").get_at((0, 0))[0], 1)
        self.assertEqual(font.render("A Y").get_size(), (24, 8))
        self.assertEqual(font.render("A Y").get_at((8, 0)).a, 0, "spaces are blank")
        # Y is built from the top of V and the stem of T.
        self.assertTrue(font.has_glyph("y"))
        self.assertEqual(font.render("Y").get_at((0, 0))[0], Font.CHARSET.index("V"))
        self.assertEqual(font.render("Y").get_at((0, 7))[0], Font.CHARSET.index("T"))
        self.assertEqual(font.render(None).get_size(), (0, 0))


class ScalingTest(unittest.TestCase):
    def test_fit_keeps_proportions(self):
        self.assertEqual(fit((464, 240), (1280, 720)).size, (1280, 662))
        self.assertEqual(fit((464, 240), (1280, 720)).top, 29)
        self.assertEqual(fit((464, 240), (1280, 720), integer=True).size, (928, 480))
        self.assertEqual(fit((464, 240), (232, 240), integer=True).size, (232, 120))


class WorldMapTest(unittest.TestCase):
    def test_walker_refuses_blocked_cells(self):
        walls = {(1, 0)}
        walker = WorldMapWalker((0, 0), lambda x, y: (x, y) in walls or x < 0 or y < 0, step_duration=0.1)
        self.assertFalse(walker.try_move(Action.RIGHT))
        self.assertFalse(walker.try_move(Action.UP))
        self.assertTrue(walker.try_move(Action.DOWN))
        self.assertFalse(walker.try_move(Action.DOWN), "one move at a time")
        walker.update(0.05)
        self.assertEqual(walker.position, pygame.Vector2(0, 8))
        walker.update(0.05)
        self.assertEqual((walker.cell, walker.moving), ((0, 1), False))
        self.assertEqual(walker.position, pygame.Vector2(0, 16))

    def test_level_tiles(self):
        self.assertEqual(level_scene_of("level1"), "level_1")
        self.assertEqual(level_scene_of("level_12"), "level_12")
        self.assertIsNone(level_scene_of("path"))

    def test_spiral_covers_the_whole_map(self):
        for columns, rows in ((29, 10), (1, 1), (3, 5)):
            covered = set()
            for x, y, dx, dy in inverse_spiral_segments(columns, rows):
                for i in range(abs(dx) + abs(dy) + 1):
                    covered.add((x + i * (dx > 0) - i * (dx < 0), y + i * (dy > 0) - i * (dy < 0)))
            self.assertEqual(covered, {(x, y) for x in range(columns) for y in range(rows)})


class RecordingScene:
    def __init__(self):
        self.calls = []

    def on_enter(self):
        self.calls.append("enter")

    def on_exit(self):
        self.calls.append("exit")

    def handle_event(self, event):
        self.calls.append("event")

    def update(self, dt):
        self.calls.append("update")

    def draw(self):
        self.calls.append("draw")


class SceneManagerTest(unittest.TestCase):
    def test_change_happens_after_the_update(self):
        manager = SceneManager()
        first, second = RecordingScene(), RecordingScene()
        manager.register("first", first)
        manager.register("second", second)
        manager.set_default_scene("first")
        manager.change_scene("second")
        self.assertIs(manager.current, first)
        manager.update(0.1)
        self.assertEqual(first.calls, ["enter", "update", "exit"])
        self.assertEqual(second.calls, ["enter"])
        self.assertEqual(manager.current_name, "second")

    def test_unknown_scene_and_quit(self):
        manager = SceneManager()
        manager.register("first", RecordingScene())
        manager.set_default_scene("first")
        with self.assertRaisesRegex(KeyError, "level_1"):
            manager.change_scene("level_1")
        manager.handle_events([Event(pygame.QUIT)])
        self.assertFalse(manager.running)


def write_level(path, columns=20, rows=8, extra=None, sheet=True, entities=None):
    """A level of the level tileset: a floor with a pit, a coin and a ? block.

    ``entities`` maps cells to entity types."""
    tiles = [["-1,-1"] * columns for _ in range(rows)]
    solid = [[False] * columns for _ in range(rows)]
    for column in range(columns):
        if column not in (8, 9):
            tiles[rows - 1][column] = "1,0"
            solid[rows - 1][column] = True
    tiles[rows - 2][4] = "4+5,3"
    tiles[rows - 4][6] = "4+4,5"
    solid[rows - 4][6] = True
    for (column, row), code in (extra or {}).items():
        tiles[row][column] = code
    data = {"tiles": tiles, "collidables": solid}
    if entities:
        data["entities"] = [{"type": kind, "x": x, "y": y} for (x, y), kind in entities.items()]
    if sheet:
        data["sheet"] = "res/sheets/level.png"
    Path(path).write_text(json.dumps(data), encoding="utf-8")
    return Path(path)


class FakeEditor:
    def __init__(self, results):
        self.results = list(results)
        self.runs = 0
        self.paused = False

    def run(self):
        self.runs += 1
        result = self.results.pop(0)
        self.paused = result.play
        return result


class LevelCatalogTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.maps = Path(self.directory.name)

    def tearDown(self):
        self.directory.cleanup()

    def test_levels_and_their_tileset(self):
        write_level(self.maps / "a_named.json")
        write_level(self.maps / "b_guessed.json", sheet=False)
        write_level(self.maps / "c_undeclared.json", extra={(0, 0): "14,5"})
        (self.maps / "d_broken.json").write_text("{", encoding="utf-8")
        write_level(self.maps / "world.json")
        catalog = LevelCatalog(maps_directory=self.maps, excluded=[self.maps / "world.json"])
        levels = {level.name: level for level in catalog.refresh()}
        self.assertEqual(sorted(levels), ["a_named", "b_guessed", "c_undeclared", "d_broken"])
        level_sheet = (PROJECT_ROOT / "res" / "sheets" / "level.png").resolve()
        self.assertEqual(levels["a_named"].sheet_path, level_sheet)
        self.assertEqual(levels["b_guessed"].sheet_path, level_sheet)
        self.assertEqual(levels["a_named"].size, (20, 8))
        self.assertIn("not declared", levels["c_undeclared"].error)
        self.assertIn("Cannot read", levels["d_broken"].error)
        self.assertIsNone(catalog.find("world"))

        world = catalog.load(levels["a_named"])
        self.assertEqual(world.tile_at(4, 6).id, "coin_frame_0")
        self.assertTrue(world.is_blocked(0, 7))
        with self.assertRaises(ValueError):
            catalog.load(levels["c_undeclared"])


def solid_floor(column, row):
    return column < 0 or column > 20 or row >= 5


class BodyTest(unittest.TestCase):
    def simulate(self, body, seconds, controls=None, is_solid=solid_floor):
        bumped = []
        for _ in range(int(seconds * 60)):
            bumped += body.update(1 / 60, controls or Controls(), is_solid)
        return bumped

    def test_falls_and_lands(self):
        body = Body(20, 0)
        self.simulate(body, 1)
        self.assertTrue(body.on_ground)
        self.assertEqual(body.y, 5 * 16 - Body.HEIGHT)

    def test_walk_run_and_walls(self):
        body = Body(20, 65)
        self.simulate(body, 1, Controls(right=True))
        self.assertAlmostEqual(body.vx, Body.WALK_SPEED)
        self.assertEqual(body.facing, 1)
        self.simulate(body, 1, Controls(right=True, run=True))
        self.assertGreater(body.vx, Body.WALK_SPEED)
        self.simulate(body, 3, Controls(right=True, run=True))
        self.assertEqual(body.x, 21 * 16 - Body.WIDTH, "stopped by the wall")
        self.simulate(body, 1)
        self.assertEqual(body.vx, 0)

    def test_jump_height_depends_on_the_key(self):
        def height(hold):
            body = Body(20, 65)
            self.simulate(body, 0.2)
            top = body.y
            body.update(1 / 60, Controls(jump=True, jump_pressed=True), solid_floor)
            for frame in range(90):
                body.update(1 / 60, Controls(jump=frame < hold), solid_floor)
                top = min(top, body.y)
            self.assertTrue(body.on_ground)
            return 65 - top

        self.assertGreater(height(60), 3 * 16)
        self.assertLess(height(1), 2 * 16)

    def test_head_bumps_the_block_above(self):
        def is_solid(column, row):
            return solid_floor(column, row) or (column, row) == (1, 2)

        body = Body(16, 65)
        self.simulate(body, 0.1)
        body.update(1 / 60, Controls(jump=True, jump_pressed=True), is_solid)
        bumped = self.simulate(body, 1, Controls(jump=True), is_solid)
        self.assertEqual(bumped, [(1, 2)])


class LevelTestCase(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.maps = Path(self.directory.name)
        self.game = Game(
            Config.from_dict({"skipIntro": True, "screen": {"width": 640, "height": 480}}),
            Save(),
            levels=LevelCatalog(maps_directory=self.maps),
        )
        self.finished = []

    def tearDown(self):
        self.directory.cleanup()

    def play(self, path, practice=False):
        catalog = self.game.context.levels
        self.game.play_level(catalog.info(path), self.finished.append, practice)
        self.game.step([], 1 / 60)
        return self.game.level_scene

    def run_frames(self, seconds, events=()):
        self.game.step(list(events), 1 / 60)
        for _ in range(int(seconds * 60)):
            self.game.step([], 1 / 60)


class PlatformLevelTest(LevelTestCase):
    def test_coin_block_and_course_clear(self):
        level = self.play(write_level(self.maps / "level.json"))
        self.assertEqual(self.game.scenes.current_name, "platform_level")
        self.assertTrue(level.body.on_ground or level.body.y < 7 * 16)
        game = self.game.context.save.game
        # Walk to the coin and under the ? block, then jump into it.
        self.run_frames(1.1, [key_event(pygame.K_d)])
        self.run_frames(0.1, [key_event(pygame.K_d, released=True)])
        self.run_frames(0.5)
        self.assertEqual(game.coins, 1, "the coin is collected")
        self.assertIsNone(level.map.tile_at(4, 6))
        level.body.x = 6 * 16 + 2
        level.body.vx = 0
        self.run_frames(0.6, [key_event(pygame.K_a)])
        self.run_frames(0.5, [key_event(pygame.K_a, released=True)])
        self.assertEqual(level.map.tile_at(6, 4).id, "block", "the ? block is emptied")
        self.assertEqual(game.coins, 2)
        # Reaching the right edge clears the course.
        level.body.x, level.body.y = 18 * 16, 6 * 16
        self.run_frames(0.5, [key_event(pygame.K_d)])
        self.assertEqual(level.message, "COURSE CLEAR")
        self.run_frames(5)
        self.assertEqual(self.finished, [True])
        self.assertGreater(game.score, 150)

    def test_falling_costs_a_life_except_in_practice(self):
        path = write_level(self.maps / "level.json")
        level = self.play(path)
        game = self.game.context.save.game
        lives = game.life
        level.body.x, level.body.y = 8 * 16 + 2, 6 * 16
        self.run_frames(4)
        self.assertEqual(game.life, lives - 1)
        self.assertEqual(level.state.name, "PLAYING", "the level restarts")
        self.assertEqual(level.map.tile_at(4, 6).id, "coin_frame_0")

        level = self.play(path, practice=True)
        level.body.x, level.body.y = 8 * 16 + 2, 6 * 16
        self.run_frames(4)
        self.assertEqual(game.life, lives - 1)

    def test_unplayable_level(self):
        path = write_level(self.maps / "level.json", extra={(0, 0): "14,5"})
        level = self.play(path)
        self.assertEqual(level.state.name, "ERROR")
        self.run_frames(0.1)
        self.run_frames(0.1, [key_event(pygame.K_a)])
        self.assertEqual(self.finished, [False])


class EntityMapTest(unittest.TestCase):
    sheet = pygame.Surface((16, 16))

    def make(self, entities):
        return Map(self.sheet, {"0,0": "grass"}, {
            "tiles": [["-1,-1"] * 3] * 2, "collidables": [[False] * 3] * 2, "entities": entities,
        })

    def test_entities_are_read_in_reading_order(self):
        world = self.make([{"type": "koopa", "x": 2, "y": 1}, {"type": "goomba", "x": 0, "y": 1},
                           {"type": "start", "x": 1, "y": 0}])
        self.assertEqual(world.entities, [
            EntitySpawn("start", 1, 0), EntitySpawn("goomba", 0, 1), EntitySpawn("koopa", 2, 1),
        ])
        self.assertEqual(self.make(None).entities, [])

    def test_invalid_entities(self):
        for entities, message in (
            ({}, "must be a list"),
            ([{"x": 0, "y": 0}], "no type"),
            ([{"type": "goomba", "x": 3, "y": 0}], "outside"),
            ([{"type": "goomba", "x": "0", "y": 0}], "invalid coordinates"),
            ([{"type": "goomba", "x": 0, "y": 0}, {"type": "koopa", "x": 0, "y": 0}], "Two entities"),
        ):
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                self.make(entities)

    def test_every_entity_of_the_editor_has_a_behaviour(self):
        self.assertEqual(set(entity_types()), set(known_types()))

    def test_unknown_entity_types_make_a_level_unplayable(self):
        with tempfile.TemporaryDirectory() as directory:
            path = write_level(Path(directory) / "level.json", entities={(3, 6): "bowser"})
            info = LevelCatalog(maps_directory=Path(directory)).info(path)
        self.assertIn("bowser", info.error)


class EntityTest(LevelTestCase):
    def entity(self, level, kind):
        return next(entity for entity in level.entities if entity.kind.id == kind)

    def drop_mario_on(self, level, entity):
        level.body.x = entity.body.x
        level.body.y = entity.rect.top - level.body.height - 1
        level.body.vy = 60.0

    def test_start_marker(self):
        level = self.play(write_level(self.maps / "level.json", entities={(12, 3): "start"}))
        self.assertEqual(level.body.rect.midbottom, (12 * 16 + 8, 4 * 16))
        self.assertEqual(level.entities, [])

    def test_stomping_a_goomba(self):
        level = self.play(write_level(self.maps / "level.json", entities={(14, 6): "goomba"}))
        goomba = self.entity(level, "goomba")
        self.run_frames(0)
        self.assertTrue(goomba.active, "the whole level is in view")
        self.run_frames(0.5)
        self.assertLess(goomba.body.x, 14 * 16, "it walks towards Mario")
        score = self.game.context.save.game.score
        self.drop_mario_on(level, goomba)
        self.run_frames(0.05)
        self.assertTrue(goomba.squashed)
        self.assertLess(level.body.vy, 0, "Mario bounces")
        self.assertEqual(self.game.context.save.game.score, score + 100)
        self.run_frames(0.6)
        self.assertNotIn(goomba, level.entities)
        self.assertEqual(level.state.name, "PLAYING")

    def test_touching_a_goomba_hurts(self):
        level = self.play(write_level(self.maps / "level.json", entities={(3, 6): "goomba"}))
        level.body.x = self.entity(level, "goomba").body.x
        self.run_frames(0.1)
        self.assertEqual(level.state.name, "DYING")

    def test_big_mario_shrinks_instead_of_dying(self):
        level = self.play(write_level(self.maps / "level.json", entities={(12, 6): "goomba"}))
        level.grow_mario(0, 0)
        self.assertTrue(level.big)
        self.assertEqual(level.body.height, Body.BIG_HEIGHT)
        self.assertEqual(self.game.context.save.game.state, PlayerState.BIG)
        self.run_frames(1)
        level.body.x = self.entity(level, "goomba").body.x
        self.run_frames(0.1)
        self.assertEqual(level.state.name, "PLAYING")
        self.assertFalse(level.big)
        self.assertEqual(self.game.context.save.game.state, PlayerState.LITTLE)
        self.assertGreater(level.invincible, 0)

    def test_koopa_shell(self):
        level = self.play(write_level(self.maps / "level.json", entities={(2, 6): "koopa", (6, 6): "goomba"}))
        koopa, goomba = self.entity(level, "koopa"), self.entity(level, "goomba")
        self.drop_mario_on(level, koopa)
        self.run_frames(0.2)
        self.assertEqual(koopa.shell, Shell.STILL)
        self.assertEqual(koopa.body.height, Koopa.SHELL_HEIGHT)
        # Mario lands and walks into the shell from the left: he kicks it.
        level.body.x = koopa.body.x - 14
        level.body.y = koopa.body.bottom - level.body.height
        level.body.vy = 0
        self.run_frames(0.3, [key_event(pygame.K_d)])
        self.run_frames(0, [key_event(pygame.K_d, released=True)])
        self.assertEqual(koopa.shell, Shell.SLIDING)
        self.assertEqual(koopa.direction, 1)
        self.assertEqual(level.state.name, "PLAYING", "kicking does not hurt")
        self.run_frames(1)
        self.assertTrue(goomba.knocked, "the shell knocks the goomba out")

    def test_mushroom_hidden_in_a_block(self):
        level = self.play(write_level(self.maps / "level.json", entities={(6, 4): "mushroom"}))
        mushroom = self.entity(level, "mushroom")
        self.assertTrue(mushroom.hidden)
        self.assertFalse(mushroom.active)
        coins = self.game.context.save.game.coins
        level.bump(6, 4)
        self.assertEqual(level.map.tile_at(6, 4).id, "block")
        self.assertEqual(self.game.context.save.game.coins, coins, "no coin: the block held the mushroom")
        self.run_frames(0.3)
        self.assertTrue(mushroom.behind_tiles)
        self.run_frames(0.5)
        self.assertLess(mushroom.body.bottom, 4 * 16 + 1, "out of the block")
        self.assertGreater(mushroom.body.x, 6 * 16, "slides to the right")
        level.body.x, level.body.y = mushroom.body.x, mushroom.body.y
        self.run_frames(1)
        self.assertTrue(level.big)
        self.assertNotIn(mushroom, level.entities)

    def test_big_mario_breaks_bricks(self):
        path = write_level(self.maps / "level.json", extra={(3, 4): "4+4,4"})
        with path.open() as file:
            data = json.load(file)
        data["collidables"][4][3] = True
        path.write_text(json.dumps(data))
        level = self.play(path)
        level.bump(3, 4)
        self.assertIsNotNone(level.map.tile_at(3, 4), "small Mario only bumps it")
        level.grow_mario(0, 0)
        level.bump(3, 4)
        self.assertIsNone(level.map.tile_at(3, 4))
        self.assertFalse(level.is_solid(3, 4))
        self.assertEqual(len(level.debris), 4)

    def test_restart_brings_the_entities_back(self):
        level = self.play(write_level(self.maps / "level.json", entities={(14, 6): "goomba"}))
        self.entity(level, "goomba").removed = True
        self.run_frames(0.1)
        self.assertEqual(level.entities, [])
        level.restart()
        self.assertEqual(len(level.entities), 1)


class EditorSessionTest(unittest.TestCase):
    def test_play_then_resume_the_same_editor(self):
        from map_editor.src.application import MapEditorApplication

        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        map_path = Path(directory.name) / "mine.json"
        sheet = PROJECT_ROOT / "res" / "sheets" / "level.png"
        application = MapEditorApplication(map_path, sheet, (10, 5), (1280, 720), playable=True)
        keys = [pygame.K_F5, pygame.K_ESCAPE]
        application.run = lambda: application.step(
            [Event(pygame.KEYDOWN, key=keys.pop(0), mod=0, unicode="")], 0.016
        )

        session = EditorSession()
        result = session._run(application)
        self.assertTrue(result.play)
        self.assertEqual(result.map_path, map_path)
        self.assertTrue(map_path.is_file(), "the map is saved before playing")
        self.assertTrue(session.paused)

        launcher = mock.MagicMock()
        launcher.return_value.run.return_value = None
        launcher.return_value.controller.window_closed = True
        with mock.patch("map_editor.src.launcher.MapEditorLauncher", launcher):
            result = session.run()
        self.assertEqual(keys, [], "the same editor ran again")
        self.assertTrue(result.quit, "then its launcher window was closed")
        self.assertFalse(session.paused)


class GameTest(unittest.TestCase):
    def setUp(self):
        # The game must find its files whatever the working directory.
        self.previous_directory = os.getcwd()
        self.directory = tempfile.TemporaryDirectory()
        os.chdir(self.directory.name)
        self.maps = Path(self.directory.name) / "maps"
        self.maps.mkdir()
        self.game = Game(
            Config.from_dict({"skipIntro": True, "screen": {"width": 640, "height": 480}}),
            Save(),
            levels=LevelCatalog(maps_directory=self.maps),
        )

    def tearDown(self):
        os.chdir(self.previous_directory)
        self.directory.cleanup()

    def run_frames(self, seconds, events=()):
        self.game.step(list(events), 1 / 60)
        for _ in range(int(seconds * 60)):
            self.game.step([], 1 / 60)

    def go_to_world_map(self):
        self.run_frames(0.1, [key_event(pygame.K_a)])
        self.run_frames(0.1, [key_event(pygame.K_RETURN)])
        self.run_frames(4.5)
        world = self.game.scenes.current
        self.run_frames(2, [key_event(pygame.K_d)])
        self.run_frames(0.1, [key_event(pygame.K_d, released=True)])
        return world

    def test_world_map_level_plays_its_map(self):
        write_level(self.maps / "level_1.json")
        self.game.context.levels.refresh()
        self.go_to_world_map()
        self.run_frames(1.5, [key_event(pygame.K_a)])
        self.assertEqual(self.game.scenes.current_name, "platform_level")
        self.run_frames(0.1, [key_event(pygame.K_ESCAPE)])
        self.run_frames(0.1, [key_event(pygame.K_ESCAPE)])
        self.assertEqual(self.game.scenes.current_name, "levels", "leaving goes back to the world map")

    def test_menu_opens_custom_levels(self):
        write_level(self.maps / "mine.json")
        game = self.game
        self.run_frames(0.1, [key_event(pygame.K_a)])
        self.run_frames(0.1, [key_event(pygame.K_s)])
        self.run_frames(0.1, [key_event(pygame.K_a)])
        self.assertEqual(game.scenes.current_name, "custom_levels")
        self.assertEqual([level.name for level in game.scenes.current.levels], ["mine"])
        self.run_frames(0.1, [key_event(pygame.K_a)])
        self.assertEqual(game.scenes.current_name, "platform_level")
        self.run_frames(0.1, [key_event(pygame.K_ESCAPE)])
        self.run_frames(0.1, [key_event(pygame.K_ESCAPE)])
        self.assertEqual(game.scenes.current_name, "custom_levels")
        self.run_frames(0.1, [key_event(pygame.K_ESCAPE)])
        self.assertEqual(game.scenes.current_name, "main_menu")

    def test_editor_play_and_resume(self):
        game = self.game
        path = write_level(self.maps / "mine.json")
        editor = FakeEditor([EditorResult(map_path=path), EditorResult(), EditorResult(quit=True)])
        game.editor = editor
        self.run_frames(0.1, [key_event(pygame.K_a)])
        self.run_frames(0.1, [key_event(pygame.K_s), key_event(pygame.K_s)])
        self.run_frames(0.1, [key_event(pygame.K_a)])
        self.assertEqual(editor.runs, 1)
        self.assertEqual(game.scenes.current_name, "platform_level")
        self.assertTrue(game.level_scene.practice)
        # Leaving the level goes back to the editor, which is then left.
        self.run_frames(0.1, [key_event(pygame.K_ESCAPE)])
        self.run_frames(0.1, [key_event(pygame.K_ESCAPE)])
        self.assertEqual(editor.runs, 2)
        self.assertEqual(game.scenes.current_name, "main_menu")
        self.assertTrue(game.running)
        # Closing the window in the editor quits the game.
        self.run_frames(0.1, [key_event(pygame.K_a)])
        self.assertEqual(editor.runs, 3)
        self.assertFalse(game.running)

    def test_play_from_title_to_world_map(self):
        game = self.game
        self.assertEqual(game.scenes.current_name, "main_menu")
        self.run_frames(0.1, [key_event(pygame.K_a)])
        self.assertTrue(game.scenes.current.ready, "confirm skips the opening")
        self.run_frames(0.1, [key_event(pygame.K_RETURN)])
        self.assertEqual(game.scenes.current_name, "animation_levels")
        self.run_frames(4.5)
        self.assertEqual(game.scenes.current_name, "levels")

        world = game.scenes.current
        start = world.walker.cell
        self.run_frames(2, [key_event(pygame.K_d)])
        self.assertEqual(world.walker.cell, world.world.find("level1").cell, "walking stops on a level")
        self.assertNotEqual(world.walker.cell, start)

        self.run_frames(0.1, [key_event(pygame.K_a)])
        self.assertEqual(game.scenes.current_name, "levels", "a level without scene does not crash")
        self.assertIsNotNone(world.message)

        self.run_frames(0.1, [key_event(pygame.K_d, released=True), key_event(pygame.K_ESCAPE)])
        self.assertEqual(game.scenes.current_name, "main_menu")
        self.run_frames(0.1, [key_event(pygame.K_a)])
        self.run_frames(4.5)
        self.assertEqual(world.walker.cell, world.world.find("level1").cell, "position kept")

    def open_settings(self):
        """From the title screen to the SETTINGS scene."""
        self.run_frames(0.1, [key_event(pygame.K_a)])
        for _ in range(3):
            self.run_frames(0.1, [key_event(pygame.K_s)])
        self.run_frames(0.1, [key_event(pygame.K_a)])
        self.assertEqual(self.game.scenes.current_name, "settings")
        return self.game.scenes.current

    def test_settings_change_the_game_and_are_saved(self):
        path = Path(self.directory.name) / "config.yaml"
        self.game.config_path = path
        settings = self.open_settings()
        # AUDIO off, then one row down to lower the music volume.
        self.run_frames(0.1, [key_event(pygame.K_d)])
        self.assertFalse(self.game.config.audio.enabled)
        self.assertFalse(self.game.context.audio.enabled)
        self.run_frames(0.1, [key_event(pygame.K_s)])
        self.run_frames(0.1, [key_event(pygame.K_q)])
        self.assertAlmostEqual(self.game.config.audio.music_volume, 0.4)
        self.assertIs(self.game.context.config, self.game.config, "the scenes see the new settings")
        self.assertEqual(settings.rows()[1], ("MUSIC VOLUME", "40"))

        self.run_frames(0.1, [key_event(pygame.K_ESCAPE)])
        self.assertEqual(self.game.scenes.current_name, "main_menu")
        self.assertEqual(Config.load(path), self.game.config, "the settings are written")

    def test_settings_rebind_a_key_and_reset(self):
        settings = self.open_settings()
        for _ in range(settings.CONTROLS_ROW):
            self.run_frames(0.1, [key_event(pygame.K_s)])
        self.run_frames(0.1, [key_event(pygame.K_a)])
        self.assertTrue(settings.controls)
        self.run_frames(0.1, [key_event(pygame.K_a)])
        self.assertTrue(settings.waiting)
        self.run_frames(0.1, [key_event(pygame.K_k)])
        self.assertEqual(self.game.config.controls.bindings[Action.UP], ("k",))
        self.assertEqual(self.game.config.controls.action_of("k"), Action.UP)
        # Escape leaves the controls, then the defaults are put back.
        self.run_frames(0.1, [key_event(pygame.K_ESCAPE)])
        self.assertFalse(settings.controls)
        self.run_frames(0.1, [key_event(pygame.K_s)])
        self.run_frames(0.1, [key_event(pygame.K_a)])
        self.assertEqual(self.game.config, Config())

    def test_rendering_is_letterboxed(self):
        self.run_frames(0.1)
        window = pygame.display.get_surface()
        self.assertEqual(window.get_at((0, 0))[:3], (0, 0, 0))
        self.assertNotEqual(window.get_at((320, 240))[:3], (0, 0, 0))

    def test_quit(self):
        self.run_frames(0.1, [key_event(pygame.K_a)])
        self.game.step([key_event(pygame.K_ESCAPE)], 1 / 60)
        self.assertFalse(self.game.running)


if __name__ == "__main__":
    unittest.main()
