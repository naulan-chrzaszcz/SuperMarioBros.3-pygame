import contextlib
import json
import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from map_editor.map_editor_cli import MapEditorCLI
from map_editor.src.application import MapEditorApplication
from map_editor.src.constantes import PROJECT_ROOT
from map_editor.src.controllers import MapController
from map_editor.src.models import EditorState, MapEditorModel, Mode, Tileset
from map_editor.src.outputs.map import Map
from map_editor.src.outputs.tile import Tile
from map_editor.src.views import Camera
from src.inputs.map import Map as GameMap

LEVEL_SHEET = PROJECT_ROOT / "res" / "sheets" / "level.png"
MENU_SHEET = PROJECT_ROOT / "res" / "sheets" / "choice_menu_stage.png"

Event = pygame.event.Event


def make_tileset(declared=((0, 0), (1, 0), (0, 1))):
    image = pygame.Surface((64, 32))
    names = {cell: f"tile_{cell[0]}_{cell[1]}" for cell in declared}
    return Tileset(image, names, Path("test.yaml"))


class MapFormatTest(unittest.TestCase):
    def test_tile_encoding_round_trip(self):
        for value in ("3,4", "1+4,2", "2,5+3&1", "0,0&3"):
            self.assertEqual(Map.encode_tile(Map.decode_tile(value)), value)

    def test_empty_and_invalid_tiles(self):
        self.assertIsNone(Map.decode_tile("-1,-1"))
        for value in ("1+2,3+4", "a,b", "-1,2", "1,2&4"):
            with self.assertRaises(ValueError):
                Map.decode_tile(value)

    def test_write_then_read_restores_everything(self):
        tiles = {(0, 0): Tile(1, 2), (2, 1): Tile(0, 0, y_frames=3, rotation=90)}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "map.json"
            Map.write(path, 3, 2, tiles, {(1, 1)})
            data = json.loads(path.read_text())
            self.assertEqual(data["tiles"], [["1,2", "-1,-1", "-1,-1"], ["-1,-1", "-1,-1", "0,0+3&1"]])
            self.assertEqual(data["collidables"], [[False, False, False], [False, True, False]])
            self.assertEqual(Map.read(path), (3, 2, tiles, {(1, 1)}))

    def test_read_rejects_ragged_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "map.json"
            path.write_text(json.dumps({"tiles": [["0,0"], []], "collidables": [[False], []]}))
            with self.assertRaises(ValueError):
                Map.read(path)

    def test_game_loads_a_map_saved_by_the_editor(self):
        pygame.init()
        sheet = pygame.Surface((32, 48))
        tiles = {(0, 0): Tile(0, 0), (1, 0): Tile(1, 0, y_frames=3, rotation=90)}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "map.json"
            Map.write(path, 2, 1, tiles, {(0, 0)})
            game_map = GameMap(sheet, {"0,0": "a", "1,0": "b"}, json.loads(path.read_text()))
        game_map.sprites.update(1.0)
        self.assertEqual(len(game_map.sprites), 2)


class MapEditorModelTest(unittest.TestCase):
    def test_edits_are_grouped_and_can_be_undone_and_redone(self):
        model = MapEditorModel(4, 4)
        with model.edit():
            model.set_tile((0, 0), Tile(1, 1))
            model.set_tile((1, 0), Tile(1, 1))
        model.set_collidable((2, 2), True)
        self.assertTrue(model.dirty)

        self.assertTrue(model.undo())
        self.assertNotIn((2, 2), model.collidables)
        self.assertTrue(model.undo())
        self.assertEqual(model.tiles, {})
        self.assertFalse(model.dirty)
        self.assertFalse(model.undo())

        self.assertTrue(model.redo())
        self.assertEqual(len(model.tiles), 2)
        model.set_tile((3, 3), Tile(0, 0))
        self.assertFalse(model.can_redo)

    def test_dirty_flag_follows_the_saved_state(self):
        model = MapEditorModel(2, 2)
        model.set_tile((0, 0), Tile(0, 0))
        with tempfile.TemporaryDirectory() as directory:
            model.save(Path(directory) / "map.json")
        self.assertFalse(model.dirty)
        model.undo()
        self.assertTrue(model.dirty)
        model.redo()
        self.assertFalse(model.dirty)

    def test_no_op_changes_are_not_recorded(self):
        model = MapEditorModel(2, 2)
        self.assertFalse(model.set_tile((0, 0), None))
        self.assertFalse(model.set_tile((5, 5), Tile(0, 0)))
        self.assertFalse(model.can_undo)

    def test_rectangle_cells_are_clipped_to_the_map(self):
        model = MapEditorModel(3, 3)
        self.assertEqual(sorted(model.cells_between((2, 2), (1, 5))), [(1, 2), (2, 2)])

    def test_resize_drops_content_outside_the_map(self):
        model = MapEditorModel(4, 4, {(3, 3): Tile(0, 0), (0, 0): Tile(0, 0)}, {(3, 0)})
        model.resize(2, 2)
        self.assertEqual(list(model.tiles), [(0, 0)])
        self.assertEqual(model.collidables, set())
        self.assertTrue(model.dirty)

    def test_undeclared_tiles(self):
        model = MapEditorModel(2, 1, {(0, 0): Tile(0, 0), (1, 0): Tile(3, 1)})
        self.assertEqual(model.undeclared_tiles(make_tileset()), {(3, 1)})


class TilesetTest(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_metadata_is_read_from_ressources_yaml(self):
        tileset = Tileset.load(MENU_SHEET)
        self.assertTrue(tileset.has_metadata)
        self.assertEqual(tileset.metadata_path.name, "choice_menu_stage.yaml")
        self.assertTrue(any(True for _ in tileset.declared_cells()))

    def test_metadata_falls_back_to_the_sidecar_yaml(self):
        tileset = Tileset.load(LEVEL_SHEET)
        self.assertEqual(tileset.metadata_path.name, "level.yaml")
        self.assertEqual(tileset.name_of(0, 0), "floor_top_left")
        self.assertFalse(tileset.is_declared(14, 5))
        self.assertEqual((tileset.columns, tileset.rows), (15, 6))


class EditorStateTest(unittest.TestCase):
    def test_selection_starts_on_a_declared_tile_and_cycles_through_them(self):
        state = EditorState(make_tileset(declared=((1, 0), (0, 1))))
        self.assertEqual((state.selection_x, state.selection_y), (1, 0))
        state.cycle_selection(1)
        self.assertEqual((state.selection_x, state.selection_y), (0, 1))

    def test_rotation_and_single_axis_animation(self):
        state = EditorState(make_tileset())
        state.rotate(-1)
        self.assertEqual(state.rotation, 270)
        state.set_frames_x(3)
        state.set_frames_y(2)
        tile = state.selected_tile()
        self.assertEqual((tile.x_frames, tile.y_frames, tile.rotation), (1, 2, 270))

    def test_pick_copies_the_tile_settings(self):
        state = EditorState(make_tileset())
        state.pick(Tile(0, 1, x_frames=2, rotation=180))
        self.assertEqual(state.selected_tile(), Tile(0, 1, x_frames=2, rotation=180))


class MapControllerTest(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.model = MapEditorModel(10, 10)
        self.state = EditorState(make_tileset())
        self.camera = Camera(10, 10, zoom=1)
        self.camera.set_viewport(pygame.Rect(0, 0, 160, 160))
        self.controller = MapController(self.model, self.state, self.camera)

    def mouse(self, kind, cell, button=None, rel=(0, 0)):
        pos = (cell[0] * 16 + 8, cell[1] * 16 + 8)
        if kind == pygame.MOUSEMOTION:
            event = Event(kind, pos=pos, rel=rel, buttons=(0, 0, 0))
        else:
            event = Event(kind, pos=pos, button=button)
        self.controller.handle_mouse(event)

    def test_a_fast_drag_paints_a_continuous_line_in_one_undo_step(self):
        self.mouse(pygame.MOUSEBUTTONDOWN, (0, 0), 1)
        self.mouse(pygame.MOUSEMOTION, (5, 0))
        self.mouse(pygame.MOUSEBUTTONUP, (5, 0), 1)
        self.assertEqual(sorted(self.model.tiles), [(x, 0) for x in range(6)])
        self.model.undo()
        self.assertEqual(self.model.tiles, {})

    def test_right_click_erases_and_middle_click_picks(self):
        self.model.set_tile((2, 2), Tile(0, 1, rotation=90))
        self.mouse(pygame.MOUSEBUTTONDOWN, (2, 2), 2)
        self.mouse(pygame.MOUSEBUTTONUP, (2, 2), 2)
        self.assertEqual(self.state.selected_tile(), Tile(0, 1, rotation=90))
        self.mouse(pygame.MOUSEBUTTONDOWN, (2, 2), 3)
        self.mouse(pygame.MOUSEBUTTONUP, (2, 2), 3)
        self.assertEqual(self.model.tiles, {})

    def test_collision_mode_toggles_collidables(self):
        self.state.mode = Mode.COLLISIONS
        self.mouse(pygame.MOUSEBUTTONDOWN, (1, 1), 1)
        self.mouse(pygame.MOUSEBUTTONUP, (1, 1), 1)
        self.assertEqual(self.model.collidables, {(1, 1)})
        self.assertEqual(self.model.tiles, {})

    def test_undeclared_tiles_are_refused(self):
        self.state.select(3, 1)
        self.mouse(pygame.MOUSEBUTTONDOWN, (0, 0), 1)
        self.mouse(pygame.MOUSEBUTTONUP, (0, 0), 1)
        self.assertEqual(self.model.tiles, {})
        self.assertIn("not declared", self.state.message)

    def test_shift_drag_fills_a_rectangle(self):
        pygame.key.set_mods(pygame.KMOD_SHIFT)
        try:
            self.mouse(pygame.MOUSEBUTTONDOWN, (1, 1), 1)
            self.mouse(pygame.MOUSEMOTION, (3, 2))
            self.assertIsNotNone(self.controller.rectangle)
            self.assertEqual(self.model.tiles, {})
            self.mouse(pygame.MOUSEBUTTONUP, (3, 2), 1)
        finally:
            pygame.key.set_mods(0)
        self.assertEqual(len(self.model.tiles), 6)
        self.model.undo()
        self.assertEqual(self.model.tiles, {})


class ApplicationTest(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.directory = tempfile.TemporaryDirectory()
        self.map_path = Path(self.directory.name) / "level.json"
        self.app = MapEditorApplication(self.map_path, LEVEL_SHEET, window_size=(1280, 720))

    def tearDown(self):
        self.directory.cleanup()

    def key(self, key, mod=0):
        self.app.step([Event(pygame.KEYDOWN, key=key, mod=mod, unicode="")], 0.016)

    def click(self, pos, button=1):
        self.app.step(
            [Event(pygame.MOUSEBUTTONDOWN, pos=pos, button=button),
             Event(pygame.MOUSEBUTTONUP, pos=pos, button=button)],
            0.016,
        )

    def test_everything_is_in_a_single_window(self):
        view = self.app.view
        self.assertEqual(view.screen.get_size(), (1280, 720))
        self.assertFalse(view.map_rect.colliderect(view.sidebar_rect))
        self.assertFalse(view.map_rect.colliderect(view.status_rect))
        self.assertTrue(view.screen.get_rect().contains(view.sidebar_rect))

    def test_paint_save_and_reload(self):
        self.click(self.app.camera.map_rect().center)
        self.assertEqual(len(self.app.model.tiles), 1)
        self.key(pygame.K_s, pygame.KMOD_CTRL)
        self.assertFalse(self.app.model.dirty)
        self.assertEqual(Map.read(self.map_path)[2], self.app.model.tiles)
        reopened = MapEditorApplication(self.map_path, LEVEL_SHEET, window_size=(1280, 720))
        self.assertEqual(reopened.model.tiles, self.app.model.tiles)

    def test_sidebar_selects_tiles_and_buttons_work(self):
        sidebar = self.app.sidebar_view
        rect = sidebar.tileset_rect
        cell_size = 16 * sidebar.tileset_scale
        self.click((rect.x + 2 * cell_size + 1, rect.y + 1))
        self.assertEqual((self.app.state.selection_x, self.app.state.selection_y), (2, 0))
        rotate = next(b for b in sidebar.buttons if b.label == "Rotate  (R)")
        self.click(rotate.rect.center)
        self.assertEqual(self.app.state.rotation, 90)

    def test_shortcuts(self):
        self.click(self.app.camera.map_rect().center)
        self.key(pygame.K_z, pygame.KMOD_CTRL)
        self.assertEqual(self.app.model.tiles, {})
        self.key(pygame.K_y, pygame.KMOD_CTRL)
        self.assertEqual(len(self.app.model.tiles), 1)
        self.key(pygame.K_c)
        self.assertIs(self.app.state.mode, Mode.COLLISIONS)
        zoom = self.app.camera.zoom
        self.key(pygame.K_PLUS)
        self.assertEqual(self.app.camera.zoom, zoom + 1)

    def test_quitting_with_unsaved_changes_needs_a_confirmation(self):
        self.click(self.app.camera.map_rect().center)
        self.key(pygame.K_ESCAPE)
        self.assertTrue(self.app.controller.running)
        self.key(pygame.K_ESCAPE)
        self.assertFalse(self.app.controller.running)

    def test_quitting_a_saved_map_is_immediate(self):
        self.app.step([Event(pygame.QUIT)], 0.016)
        self.assertFalse(self.app.controller.running)

    def test_existing_map_can_be_resized(self):
        Map.write(self.map_path, 5, 3, {(4, 2): Tile(0, 0)}, set())
        app = MapEditorApplication(self.map_path, LEVEL_SHEET, (3, 3), (1280, 720))
        self.assertEqual((app.model.columns, app.model.rows), (3, 3))
        self.assertEqual(app.model.tiles, {})
        self.assertTrue(app.model.dirty)


class CLITest(unittest.TestCase):
    def test_arguments(self):
        cli = MapEditorCLI.from_args(["map.json", "--size", "100x15"])
        self.assertEqual(cli.map_path, Path("map.json"))
        self.assertEqual(cli.size, (100, 15))
        self.assertIsNone(MapEditorCLI.from_args(["map.json"]).size)

    def test_invalid_size_is_rejected(self):
        with self.assertRaises(SystemExit), open(os.devnull, "w") as devnull:
            with contextlib.redirect_stderr(devnull):
                MapEditorCLI.from_args(["map.json", "--size", "0x3"])


if __name__ == "__main__":
    unittest.main()
