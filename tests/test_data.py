"""The data files that configure the game: rules, sprites, entities, tile
behaviours, level settings and sounds."""

import json
import tempfile
import unittest
from pathlib import Path

import pygame
import test_game
from test_game import LevelTestCase, key_event, write_level

from src.animation import Animation, SpriteBank
from src.entities.catalog import EntityType, entity_types, load_entity_types, parse_entity_type
from src.entities.goomba import Goomba
from src.entities.koopa import Koopa
from src.entities.spawner import ENTITY_CLASSES, validate_entity_types
from src.game import Game
from src.inputs.config import Action, Config
from src.inputs.map import LevelSettings, TileBehaviour
from src.inputs.ressources import Ressources
from src.inputs.rules import Rules
from src.inputs.save import Save
from src.inputs.sprites import load_sprite_specs, parse_animation
from src.inputs.tuning import check, constant_name, setting_key, tune
from src.levels import LevelCatalog
from src.platformer import Body
from src.scenes import LevelsScene, PlatformLevelScene


def setUpModule():
    test_game.setUpModule()


class TuningTest(unittest.TestCase):
    class Thing:
        NOT_TUNABLE = ("NAME",)
        NAME = "thing"
        SPEED = 1.0
        LIVES = 3
        FLYING = False
        SCORES = (1, 2)
        SKY_COLOR = (0, 0, 0)

    def test_names(self):
        self.assertEqual(constant_name("walkSpeed"), "WALK_SPEED")
        self.assertEqual(constant_name("walk_speed"), "WALK_SPEED")
        self.assertEqual(setting_key("WALK_SPEED"), "walkSpeed")

    def test_values_are_checked(self):
        values = check(self.Thing, {"speed": 2, "scores": [5, 6, 7], "skyColor": [255, 0, 0]}, "test")
        self.assertEqual(values, {"SPEED": 2.0, "SCORES": (5, 6, 7), "SKY_COLOR": (255, 0, 0)})
        for settings in ({"lives": 1.5}, {"flying": 1}, {"speed": "fast"}, {"name": "other"}, {"unknown": 1}):
            with self.assertRaises(ValueError, msg=settings):
                check(self.Thing, settings, "test")
        with self.assertRaisesRegex(ValueError, "known: .*speed"):
            check(self.Thing, {"sped": 1}, "test")

    def test_tune_changes_the_instance_only(self):
        thing = tune(self.Thing(), {"lives": 5}, "test")
        self.assertEqual(thing.LIVES, 5)
        self.assertEqual(self.Thing.LIVES, 3)


class RulesTest(unittest.TestCase):
    def test_project_rules_are_valid(self):
        rules = Rules.load()
        check(Body, rules.player, "player")
        check(PlatformLevelScene, rules.level, "level")
        check(LevelsScene, rules.world_map, "worldMap")

    def test_the_file_gives_the_defaults_of_the_code(self):
        rules = Rules.load()
        sections = ((Body, rules.player), (PlatformLevelScene, rules.level),
                    (LevelsScene, rules.world_map))
        for cls, settings in sections:
            for name, value in check(cls, settings, cls.__name__).items():
                self.assertEqual(value, getattr(cls, name), f"{cls.__name__}.{name}")

    def test_unknown_sections(self):
        with self.assertRaises(ValueError):
            Rules.from_dict({"mario": {}})
        self.assertEqual(Rules.load(Path("missing.yaml")).player, {})

    def test_errors_are_reported_when_the_game_starts(self):
        with self.assertRaisesRegex(ValueError, "walkSped"):
            Game(Config.from_dict({"skipIntro": True}), Save(),
                 rules=Rules.from_dict({"player": {"walkSped": 1}}))
        with self.assertRaisesRegex(ValueError, "unknown music"):
            Game(Config.from_dict({"skipIntro": True}), Save(),
                 rules=Rules.from_dict({"level": {"music": "nope"}}))


class SpritesTest(unittest.TestCase):
    def test_animation_forms(self):
        self.assertEqual(parse_animation([0, 0, 16, 16], "a").frames, ((0, 0, 16, 16),))
        self.assertEqual(len(parse_animation([[0, 0, 16, 16], [16, 0, 16, 16]], "a").frames), 2)
        spec = parse_animation({"frames": [[0, 0, 8, 8]], "period": 0.5, "mirror": True}, "a")
        self.assertEqual((spec.period, spec.mirror), (0.5, True))
        for wrong in ([0, 0, 16], {"period": 1}, "walk"):
            with self.assertRaises(ValueError):
                parse_animation(wrong, "a")

    def test_mirrored_animation(self):
        frame = pygame.Surface((2, 1))
        frame.set_at((0, 0), (255, 0, 0))
        animation = Animation([frame], period=0.1, mirror=True)
        self.assertEqual(animation.image(0.0).get_at((0, 0))[:3], (255, 0, 0))
        self.assertEqual(animation.image(0.15).get_at((1, 0))[:3], (255, 0, 0), "played flipped")
        self.assertEqual(animation.image(0.0, facing=1).get_at((1, 0))[:3], (255, 0, 0))

    def test_every_sprite_of_the_project_is_cut(self):
        bank = SpriteBank(Ressources.load())
        for name in load_sprite_specs():
            self.assertTrue(bank.animations(name))
        self.assertEqual(bank.image("hud", "frame").get_size(), (154, 30))
        self.assertEqual(bank.position("hud", "score"), (50, 16))

    def test_frames_outside_the_image(self):
        bank = SpriteBank(Ressources.load(), {})
        spec = parse_animation([0, 0, 9999, 16], "a")
        with self.assertRaisesRegex(ValueError, "outside"):
            bank.build("goomba", {"walk": spec})


class EntityDataTest(unittest.TestCase):
    def test_project_entities_are_valid(self):
        validate_entity_types(entity_types())
        self.assertEqual(entity_types()["red_koopa"].behaviour, "koopa")
        self.assertEqual(entity_types()["goomba"].editor_frame, (0, 0, 16, 16))

    def test_invalid_entities(self):
        with self.assertRaisesRegex(ValueError, "unknown key"):
            parse_entity_type({"id": "a", "image": "goomba", "frame": [0, 0, 16, 16], "speed": 3})
        with self.assertRaisesRegex(ValueError, "frame or animations"):
            parse_entity_type({"id": "a", "image": "goomba"})
        with self.assertRaisesRegex(ValueError, "unknown behaviour"):
            validate_entity_types({"a": EntityType("a", "A", "goomba", "dragon", (0, 0, 16, 16))})
        goomba = parse_entity_type({"id": "g", "behaviour": "goomba", "image": "goomba",
                                    "animations": {"walk": [0, 0, 16, 16]}})
        with self.assertRaisesRegex(ValueError, "squashed"):
            validate_entity_types({"g": goomba})
        with self.assertRaisesRegex(ValueError, "speeed"):
            validate_entity_types({"g": parse_entity_type({
                "id": "g", "behaviour": "goomba", "image": "goomba", "settings": {"speeed": 1},
                "animations": {"walk": [0, 0, 16, 16], "squashed": [16, 0, 16, 16]}})})

    def test_duplicated_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "entities.yaml"
            path.write_text("entities:\n" + "  - {id: a, image: goomba, frame: [0, 0, 16, 16]}\n" * 2)
            with self.assertRaisesRegex(ValueError, "two entities"):
                load_entity_types(path)

    def test_every_behaviour_has_its_animations(self):
        for kind in entity_types().values():
            cls = ENTITY_CLASSES.get(kind.behaviour)
            if cls is not None:
                self.assertLessEqual(set(cls.ANIMATIONS), set(kind.animations), kind.id)


class TileBehaviourTest(unittest.TestCase):
    def test_parse_and_guess(self):
        self.assertEqual(TileBehaviour.parse("question_block", "block"),
                         TileBehaviour("question_block", "block"))
        with self.assertRaises(ValueError):
            TileBehaviour.parse("lava")
        self.assertEqual(TileBehaviour.guess("coin_frame_2").kind, "coin")
        self.assertIsNone(TileBehaviour.guess("floor_top"))

    def test_level_tileset_declares_its_behaviours(self):
        catalog = LevelCatalog()
        with tempfile.TemporaryDirectory() as directory:
            level = catalog.load(catalog.info(write_level(Path(directory) / "a.json")))
        self.assertEqual(level.names_with("coin")[0], "coin_frame_0")
        self.assertEqual(level.behaviour_of(level.tile_at(6, 4)), TileBehaviour("question_block", "block"))

    def test_level_settings(self):
        settings = LevelSettings.parse(
            {"name": "Hills", "timeLimit": 200, "sky": [0, 0, 0], "music": "title"})
        self.assertEqual((settings.name, settings.time_limit, settings.sky), ("Hills", 200, (0, 0, 0)))
        for wrong in ({"timeLimit": 0}, {"timeLimit": "300"}, {"weather": "rain"}, {"sky": "blue-ish"}):
            with self.assertRaises(ValueError, msg=wrong):
                LevelSettings.parse(wrong)


def add_level_block(path, level):
    data = json.loads(path.read_text())
    data["level"] = level
    path.write_text(json.dumps(data))
    return path


class DataInGameTest(LevelTestCase):
    def test_level_settings_of_the_map(self):
        path = add_level_block(write_level(self.maps / "level.json"),
                               {"name": "Night hills", "timeLimit": 120,
                                "sky": [16, 24, 64], "music": "title"})
        self.assertEqual(self.game.context.levels.info(path).title, "Night hills")
        level = self.play(path)
        self.assertLessEqual(level.time_left, 120)
        self.assertEqual(level.sky, (16, 24, 64))
        self.assertEqual(self.game.context.audio.music, "title")

    def test_unknown_music_is_an_error(self):
        path = add_level_block(write_level(self.maps / "level.json"), {"music": "nope"})
        level = self.play(path)
        self.assertIsNotNone(level.error)
        self.assertIn("nope", level.error)

    def test_music_resumes_when_the_editor_is_closed(self):
        from src.editor_bridge import EditorResult

        game = self.game
        game.editor = test_game.FakeEditor([EditorResult()])
        game.context.audio.play_music("title")
        game.open_editor()
        game.step([], 1 / 60)
        self.assertEqual(game.editor.runs, 1)
        self.assertEqual(game.scenes.current_name, "main_menu")
        self.assertEqual(game.context.audio.music, "title")

    def test_defaults_come_from_the_rules(self):
        level = self.play(write_level(self.maps / "level.json"))
        self.assertEqual(level.sky, PlatformLevelScene.SKY_COLOR)
        self.assertEqual(self.game.context.audio.music, "overworld")

    def test_sounds_are_played_on_events(self):
        level = self.play(write_level(self.maps / "level.json"))
        audio = self.game.context.audio
        self.run_frames(0.5)
        level.on_action(Action.CONFIRM)
        self.run_frames(0.1)
        self.assertIn("jump", audio.history)
        level.on_action(Action.BACK)
        self.assertIn("pause", audio.history)

    def test_hurt_and_goal_tiles(self):
        level = self.play(write_level(self.maps / "level.json"))
        # The coin becomes a goal: touching it clears the course.
        level.map.behaviours["coin_frame_0"] = TileBehaviour("goal")
        level.body.x, level.body.y = 4 * 16 + 2, 6 * 16
        self.run_frames(0.1)
        self.assertEqual(level.message, "COURSE CLEAR")

        level = self.play(write_level(self.maps / "level.json"))
        level.map.behaviours["coin_frame_0"] = TileBehaviour("hurt")
        level.body.x, level.body.y = 4 * 16 + 2, 6 * 16
        self.run_frames(0.1)
        self.assertEqual(level.state.name, "DYING")


class RulesInGameTest(LevelTestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.maps = Path(self.directory.name)
        rules = Rules.from_dict({"player": {"walkSpeed": 40},
                                 "level": {"timeLimit": 42, "skyColor": [1, 2, 3]}})
        self.game = Game(
            Config.from_dict({"skipIntro": True, "screen": {"width": 640, "height": 480}}),
            Save(),
            levels=LevelCatalog(maps_directory=self.maps),
            rules=rules,
        )
        self.finished = []

    def test_rules_change_mario_and_the_level(self):
        level = self.play(write_level(self.maps / "level.json"))
        self.assertEqual(level.body.WALK_SPEED, 40)
        self.assertEqual(Body.WALK_SPEED, 90, "the defaults are not changed")
        self.assertLessEqual(level.time_left, 42)
        self.assertEqual(level.sky, (1, 2, 3))
        self.run_frames(1, [key_event(pygame.K_d)])
        self.assertAlmostEqual(level.body.vx, 40)


class EntitySettingsTest(LevelTestCase):
    def test_settings_and_red_koopa_turning_at_ledges(self):
        # A floor from column 2 to 7, then the pit.
        path = write_level(self.maps / "level.json", entities={(7, 6): "red_koopa", (0, 6): "start"})
        level = self.play(path)
        koopa = next(entity for entity in level.entities if entity.kind.id == "red_koopa")
        self.assertIsInstance(koopa, Koopa)
        self.assertTrue(koopa.TURN_AT_LEDGES)
        self.assertFalse(Koopa.TURN_AT_LEDGES)
        koopa.activate(level)
        koopa.direction = 1
        for _ in range(120):
            koopa.update(1 / 60, level)
        self.assertLess(koopa.body.bottom, 7 * 16 + 1, "it did not fall in the pit")
        self.assertEqual(koopa.direction, -1)

    def test_goomba_speed_comes_from_the_settings(self):
        kind = entity_types()["goomba"]
        goomba = Goomba(kind, self.game.context.sprites, 3, 6)
        self.assertEqual(goomba.SPEED, kind.settings["speed"])
        faster = EntityType(**{**kind.__dict__, "settings": {"speed": 64}})
        self.assertEqual(Goomba(faster, self.game.context.sprites, 3, 6).SPEED, 64)


if __name__ == "__main__":
    unittest.main()
