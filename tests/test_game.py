import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from src.font import Font
from src.game import Game, fit
from src.inputs.config import Action, Config
from src.inputs.map import Map, TileCode
from src.inputs.ressources import Ressources
from src.inputs.save import PlayerState, Save
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
        world = self.make([["1,0", "0,0", "0,1"], ["0,0", "-1,-1", "0,0"]], [[False, True, False], [False] * 3])
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

    def test_unknown_settings_are_reported(self):
        for data in ({"skipIntr": True}, {"screen": {"widht": 3}}, {"display": {"width": 0}}, {"controls": {"jump": "x"}}):
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
        self.assertEqual(font.render("A Y").get_at((8, 0)).a, 0)
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


class GameTest(unittest.TestCase):
    def setUp(self):
        # The game must find its files whatever the working directory.
        self.previous_directory = os.getcwd()
        self.directory = tempfile.TemporaryDirectory()
        os.chdir(self.directory.name)
        self.game = Game(Config.from_dict({"skipIntro": True, "screen": {"width": 640, "height": 480}}), Save())

    def tearDown(self):
        os.chdir(self.previous_directory)
        self.directory.cleanup()

    def run_frames(self, seconds, events=()):
        self.game.step(list(events), 1 / 60)
        for _ in range(int(seconds * 60)):
            self.game.step([], 1 / 60)

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
