import json
import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from map_editor.src.commands_surface import CommandsSurface
from map_editor.src.controllers import MapEditorController
from map_editor.src.models import MapEditorModel
from map_editor.src.outputs.map import Map
from map_editor.src.outputs.tile import Tile
from map_editor.src.tile_selection_surface import TileSelectionSurface
from map_editor.src.views import MapEditorView
from src.inputs.map import Map as GameMap


class MapFormatTests(unittest.TestCase):
    def test_tile_encoding_round_trip(self):
        tile = Tile(4, 5, 3, 1, 270)

        encoded = Map.encode_tile(tile)

        self.assertEqual(encoded, "4+3,5&3")
        self.assertEqual(Map.decode_tile(encoded), tile)

    def test_empty_tile_decodes_to_none(self):
        self.assertIsNone(Map.decode_tile("-1,-1"))

    def test_invalid_two_axis_animation_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "only one axis"):
            Map.decode_tile("1+2,2+2")

    def test_write_creates_game_compatible_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "maps" / "level.json"
            tile = Tile(2, 3, 1, 2, 90)
            collidable = pygame.Rect(16, 0, 16, 16)

            Map.write(path, {(0, 0): tile}, {(16, 0): collidable}, 32, 16)

            with path.open(encoding="utf-8") as file:
                data = json.load(file)
            self.assertEqual(data["tiles"], [["2,3+2&1", "-1,-1"]])
            self.assertEqual(data["collidables"], [[False, True]])


class MapEditorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.sheet = pygame.Surface((32, 32))
        self.sheet.fill((255, 255, 255))

    def test_load_restores_every_tile_and_collision(self):
        data = {
            "tiles": [["0,0", "1,0"], ["0,1", "1,1"]],
            "collidables": [[True, False], [False, True]],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "level.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            model = MapEditorModel(32, 32, self.sheet)

            model.load(path)

        self.assertEqual(len(model.tiles), 4)
        self.assertEqual(set(model.collidables), {(0, 0), (16, 16)})
        self.assertFalse(model.dirty)

    def test_controller_places_erases_and_marks_collision(self):
        model = MapEditorModel(32, 32, self.sheet)
        view = MapEditorView((32, 32))
        commands = CommandsSurface(200, 300)
        selection = TileSelectionSurface(self.sheet)
        controller = MapEditorController(model, view, commands, selection)

        controller.handle_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN, button=1, pos=(10, 10)
            )
        )
        self.assertIn((0, 0), model.tiles)

        controller.handle_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN, button=3, pos=(10, 10)
            )
        )
        self.assertNotIn((0, 0), model.tiles)

        commands.toggle_collidable()
        controller.handle_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN, button=1, pos=(10, 10)
            )
        )
        self.assertIn((0, 0), model.collidables)
        controller.update()

    def test_game_loads_rotated_vertical_animation_exported_by_editor(self):
        sheet = pygame.Surface((16, 32))
        sheet.fill((255, 255, 255))
        game_map = GameMap(
            sheet,
            {"0,0": "animated"},
            {
                "tiles": [["0,0+2&1"]],
                "collidables": [[False]],
            },
        )

        game_map.sprites.update(1.0)

        self.assertEqual(len(game_map.sprites), 1)

    def test_load_rejects_wrong_dimensions_without_changing_model(self):
        data = {
            "tiles": [["0,0"]],
            "collidables": [[False]],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "level.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            model = MapEditorModel(32, 32, self.sheet)
            model.add_tile(0, 0, Tile(0, 0, 1, 1, 0))

            with self.assertRaisesRegex(ValueError, "expected 2x2"):
                model.load(path)

        self.assertIn((0, 0), model.tiles)


if __name__ == "__main__":
    unittest.main()
