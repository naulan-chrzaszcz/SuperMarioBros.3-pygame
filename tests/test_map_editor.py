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
from map_editor.src.launcher import MapEditorLauncher
from map_editor.src.models import Clipboard, EditorState, LauncherModel, MapEditorModel, Mode, Tileset
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

    def test_play_saves_the_map_with_its_tileset_and_leaves(self):
        self.click(self.app.camera.map_rect().center)
        self.key(pygame.K_F5)
        self.assertTrue(self.app.controller.running, "the standalone editor cannot play")
        self.assertTrue(self.app.model.dirty)

        self.app.controller.can_play = True
        self.key(pygame.K_F5)
        self.assertFalse(self.app.controller.running)
        self.assertTrue(self.app.controller.play_requested)
        self.assertFalse(self.app.model.dirty)
        self.assertEqual(Map.read_sheet(self.map_path), LEVEL_SHEET.resolve())

        self.app.resume()
        self.assertTrue(self.app.controller.running)
        self.assertFalse(self.app.controller.play_requested)
        self.assertEqual(len(self.app.model.tiles), 1, "the edits are kept")

    def test_quitting_a_saved_map_is_immediate(self):
        self.app.step([Event(pygame.QUIT)], 0.016)
        self.assertFalse(self.app.controller.running)

    def test_map_outside_a_sheet_without_metadata_opens_with_a_warning(self):
        Map.write(self.map_path, 2, 1, {(0, 0): Tile(40, 40)}, set())
        sheet = PROJECT_ROOT / "res" / "sheets" / "mushroomRed.png"
        app = MapEditorApplication(self.map_path, sheet, window_size=(1280, 720))
        self.assertIn("outside the tileset image", app.state.message)
        app.state.select(0, 0)
        app.state.pick(Tile(40, 40))
        app.render()
        self.key(pygame.K_s, pygame.KMOD_CTRL)
        self.assertIn("outside the tileset image", app.state.message)

    def test_existing_map_can_be_resized(self):
        Map.write(self.map_path, 5, 3, {(4, 2): Tile(0, 0)}, set())
        app = MapEditorApplication(self.map_path, LEVEL_SHEET, (3, 3), (1280, 720))
        self.assertEqual((app.model.columns, app.model.rows), (3, 3))
        self.assertEqual(app.model.tiles, {})
        self.assertTrue(app.model.dirty)


class ClipboardTest(unittest.TestCase):
    def test_copy_paste_keeps_tiles_and_collisions_and_skips_empty_cells(self):
        model = MapEditorModel(6, 4, {(1, 1): Tile(0, 0), (4, 3): Tile(1, 0)}, {(2, 1)})
        clipboard = model.copy((1, 1, 2, 2))
        self.assertEqual((clipboard.columns, clipboard.rows), (2, 2))
        self.assertEqual(clipboard.tiles, {(0, 0): Tile(0, 0)})
        self.assertEqual(clipboard.collidables, {(1, 0)})

        model.set_tile((4, 2), Tile(0, 1))
        model.paste(clipboard, (3, 2))
        self.assertEqual(model.tiles[(3, 2)], Tile(0, 0))
        self.assertIn((4, 2), model.collidables)
        # (4, 2) is solid in the clipboard, so its tile is replaced by "no tile".
        self.assertNotIn((4, 2), model.tiles)
        # Transparent cells of the clipboard leave the map untouched.
        self.assertEqual(model.tiles[(4, 3)], Tile(1, 0))
        model.undo()
        self.assertEqual(model.tiles[(4, 2)], Tile(0, 1))
        self.assertNotIn((3, 2), model.tiles)

    def test_paste_is_clipped_and_skips_undeclared_tiles(self):
        clipboard = Clipboard(2, 1, {(0, 0): Tile(0, 0), (1, 0): Tile(3, 1)})
        model = MapEditorModel(2, 2)
        self.assertEqual(model.paste(clipboard, (0, 0), make_tileset()), 1)
        self.assertEqual(model.tiles, {(0, 0): Tile(0, 0)})
        model.paste(clipboard, (1, 1))
        self.assertEqual(model.tiles[(1, 1)], Tile(0, 0))

    def test_clear_removes_a_region_in_one_undo_step(self):
        model = MapEditorModel(3, 3, {(0, 0): Tile(0, 0), (1, 1): Tile(0, 0)}, {(2, 2)})
        model.clear((0, 0, 2, 2))
        self.assertEqual((model.tiles, model.collidables), ({}, set()))
        model.undo()
        self.assertEqual(len(model.tiles), 2)
        self.assertEqual(model.collidables, {(2, 2)})

    def test_rotation_turns_the_block_and_its_tiles_counter_clockwise(self):
        clipboard = Clipboard(3, 2, {(2, 0): Tile(0, 0), (0, 1): Tile(1, 0, rotation=270)}, frozenset({(0, 0)}))
        rotated = clipboard.rotated()
        self.assertEqual((rotated.columns, rotated.rows), (2, 3))
        self.assertEqual(rotated.tiles, {(0, 0): Tile(0, 0, rotation=90), (1, 2): Tile(1, 0)})
        self.assertEqual(rotated.collidables, {(0, 2)})
        self.assertEqual(clipboard.rotated(4), clipboard)
        self.assertEqual(clipboard.rotated(-1).rotated(1), clipboard)

    def test_select_copy_and_paste_in_the_editor(self):
        pygame.init()
        with tempfile.TemporaryDirectory() as directory:
            map_path = Path(directory) / "map.json"
            Map.write(map_path, 10, 5, {(0, 0): Tile(0, 0), (1, 0): Tile(1, 0)}, {(1, 0)})
            app = MapEditorApplication(map_path, LEVEL_SHEET, window_size=(1280, 720))
        camera = app.camera

        def at(cell):
            x, y = camera.cell_to_screen(cell)
            return x + 2, y + 2

        def key(key, mod=0):
            app.step([Event(pygame.KEYDOWN, key=key, mod=mod, unicode="")], 0.016)

        key(pygame.K_s)
        self.assertIs(app.state.mode, Mode.SELECT)
        app.step([
            Event(pygame.MOUSEBUTTONDOWN, pos=at((0, 0)), button=1),
            Event(pygame.MOUSEMOTION, pos=at((1, 0)), rel=(1, 0), buttons=(1, 0, 0)),
            Event(pygame.MOUSEBUTTONUP, pos=at((1, 0)), button=1),
        ], 0.016)
        self.assertEqual(app.state.region, (0, 0, 1, 0))
        key(pygame.K_c, pygame.KMOD_CTRL)
        key(pygame.K_v, pygame.KMOD_CTRL)
        self.assertTrue(app.state.pasting)
        app.step([Event(pygame.MOUSEBUTTONDOWN, pos=at((5, 3)), button=1),
                  Event(pygame.MOUSEBUTTONUP, pos=at((5, 3)), button=1)], 0.016)
        self.assertEqual(app.model.tiles[(5, 3)], Tile(0, 0))
        self.assertEqual(app.model.tiles[(6, 3)], Tile(1, 0))
        self.assertIn((6, 3), app.model.collidables)

        key(pygame.K_ESCAPE)
        self.assertFalse(app.state.pasting)
        key(pygame.K_ESCAPE)
        self.assertIsNone(app.state.region)
        self.assertTrue(app.controller.running)

        app.map_controller.select_all()
        key(pygame.K_x, pygame.KMOD_CTRL)
        self.assertEqual(app.model.tiles, {})
        key(pygame.K_z, pygame.KMOD_CTRL)
        self.assertEqual(len(app.model.tiles), 4)


class LauncherTest(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.directory = tempfile.TemporaryDirectory()
        root = Path(self.directory.name)
        self.maps = root / "maps"
        self.maps.mkdir()
        self.settings = root / "settings.json"
        # Uses a tile only declared in choice_menu_stage.yaml.
        menu_cell = next(iter(Tileset.load(MENU_SHEET).names))
        Map.write(self.maps / "menu.json", 4, 3, {(0, 0): Tile(*menu_cell)}, set())
        Map.write(self.maps / "world.json", 30, 15, {}, set())
        (self.maps / "broken.json").write_text("{")

    def tearDown(self):
        self.directory.cleanup()

    def model(self):
        return LauncherModel(maps_directory=self.maps, settings_file=self.settings)

    def test_maps_are_listed_with_their_size_and_tileset(self):
        model = self.model()
        self.assertEqual([entry.path.name for entry in model.maps], ["broken.json", "menu.json", "world.json"])
        self.assertIsNotNone(model.maps[0].error)
        self.assertTrue(model.sheets[0].has_metadata)
        model.select_map(1)
        self.assertEqual((model.width, model.height), ("4", "3"))
        self.assertEqual(model.sheet.path.name, "choice_menu_stage.png")
        model.select_map(2)
        self.assertEqual(model.sheet.path.name, "level.png")

    def test_the_tileset_recorded_in_the_map_is_preferred(self):
        Map.write(self.maps / "world.json", 30, 15, {}, set(), MENU_SHEET)
        model = self.model()
        model.select_map(2)
        self.assertEqual(model.sheet.path.name, "choice_menu_stage.png")
        self.assertEqual(json.loads((self.maps / "world.json").read_text())["sheet"],
                         "res/sheets/choice_menu_stage.png")

    def test_unreadable_maps_cannot_be_opened(self):
        model = self.model()
        model.select_map(0)
        with self.assertRaises(ValueError):
            model.request()

    def test_opening_remembers_the_tileset_and_can_resize(self):
        model = self.model()
        model.select_map(2)
        model.select_sheet(next(i for i, s in enumerate(model.sheets) if s.path.name == "choice_menu_stage.png"))
        model.width = "40"
        request = model.request()
        self.assertEqual(request.size, (40, 15))
        self.assertEqual(request.sheet_path.name, "choice_menu_stage.png")

        reopened = self.model()
        self.assertEqual(reopened.selected_map.path.name, "world.json")
        self.assertEqual(reopened.sheet.path.name, "choice_menu_stage.png")
        self.assertIsNone(reopened.request().size)

    def test_new_map_validation_and_creation(self):
        model = self.model()
        model.select_new()
        for name, width in (("", "29"), ("bad name", "29"), ("menu", "29"), ("ok", "0"), ("ok", "")):
            model.name, model.width = name, width
            with self.assertRaises(ValueError):
                model.request()
        model.name, model.width, model.height = "level_2", "50", "12"
        request = model.request()
        self.assertEqual(request.map_path, self.maps / "level_2.json")
        self.assertEqual(Map.read(request.map_path)[:2], (50, 12))

    def test_create_a_map_with_the_mouse_and_keyboard(self):
        launcher = MapEditorLauncher(self.model(), (1000, 640))
        view = launcher.view
        launcher.step([Event(pygame.MOUSEBUTTONDOWN, pos=view.map_list.rect.move(5, 5).topleft, button=1)], 0.1)
        self.assertTrue(launcher.model.is_new)
        self.assertTrue(view.name_field.focused)
        launcher.step([
            Event(pygame.TEXTINPUT, text="new level!"),
            Event(pygame.KEYDOWN, key=pygame.K_BACKSPACE, mod=0, unicode=""),
            Event(pygame.KEYDOWN, key=pygame.K_TAB, mod=0, unicode=""),
            Event(pygame.KEYDOWN, key=pygame.K_BACKSPACE, mod=pygame.KMOD_CTRL, unicode=""),
            Event(pygame.TEXTINPUT, text="6x0"),
        ], 0.1)
        self.assertEqual((launcher.model.name, launcher.model.width), ("newleve", "60"))
        launcher.step([Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0, unicode="")], 0.1)
        self.assertFalse(launcher.controller.running)
        self.assertEqual(launcher.controller.result.map_path.name, "newleve.json")

    def test_double_click_opens_a_map_and_errors_are_shown(self):
        launcher = MapEditorLauncher(self.model(), (1000, 640))
        list_box = launcher.view.map_list
        broken = list_box.rect.move(5, 5 + list_box.item_height).topleft
        menu = list_box.rect.move(5, 5 + 2 * list_box.item_height).topleft
        click = [Event(pygame.MOUSEBUTTONDOWN, pos=broken, button=1)]
        launcher.step(click + click, 0.0)
        self.assertTrue(launcher.controller.running)
        self.assertIn("cannot be read", launcher.model.message)
        click = [Event(pygame.MOUSEBUTTONDOWN, pos=menu, button=1)]
        launcher.step(click, 0.1)
        launcher.step(click, 0.1)
        self.assertEqual(launcher.controller.result.map_path.name, "menu.json")

    def test_escape_quits_without_result(self):
        launcher = MapEditorLauncher(self.model(), (1000, 640))
        launcher.step([Event(pygame.KEYDOWN, key=pygame.K_ESCAPE, mod=0, unicode="")], 0.1)
        self.assertFalse(launcher.controller.running)
        self.assertIsNone(launcher.controller.result)


class CLITest(unittest.TestCase):
    def test_arguments(self):
        cli = MapEditorCLI.from_args(["map.json", "--size", "100x15"])
        self.assertEqual(cli.map_path, Path("map.json"))
        self.assertEqual(cli.size, (100, 15))
        self.assertIsNone(MapEditorCLI.from_args(["map.json"]).size)

    def test_the_tileset_recorded_in_the_map_is_the_default(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "menu.json"
            Map.write(path, 2, 2, {}, set(), MENU_SHEET)
            self.assertEqual(MapEditorCLI.from_args([str(path)]).sheet_path, MENU_SHEET.resolve())
            self.assertEqual(
                MapEditorCLI.from_args([str(path), "--sheet", str(LEVEL_SHEET)]).sheet_path, LEVEL_SHEET
            )
        self.assertEqual(MapEditorCLI.from_args(["missing.json"]).sheet_path.name, "level.png")

    def test_invalid_size_is_rejected(self):
        with self.assertRaises(SystemExit), open(os.devnull, "w") as devnull:
            with contextlib.redirect_stderr(devnull):
                MapEditorCLI.from_args(["map.json", "--size", "0x3"])


if __name__ == "__main__":
    unittest.main()


class EntityEditorTest(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / "map.json"

    def tearDown(self):
        self.directory.cleanup()

    def test_entity_types_come_from_the_shared_catalog(self):
        state = EditorState(make_tileset())
        ids = [entity.id for entity in state.entity_types]
        self.assertEqual(ids[0], "start")
        self.assertTrue({"goomba", "koopa", "mushroom", "one_up"} <= set(ids))
        self.assertEqual(state.unique_entities, {"start"})
        for entity in state.entity_types:
            self.assertTrue(entity.sheet_path.is_file(), entity.id)

    def test_entities_are_written_and_read_back(self):
        entities = {(3, 1): "goomba", (0, 1): "start"}
        Map.write(self.path, 4, 2, {}, set(), entities=entities)
        data = json.loads(self.path.read_text())
        self.assertEqual(data["entities"], [
            {"type": "start", "x": 0, "y": 1}, {"type": "goomba", "x": 3, "y": 1},
        ])
        self.assertEqual(Map.read_entities(self.path), entities)
        self.assertEqual(MapEditorModel.from_file(self.path).entities, entities)

    def test_a_map_without_entities_has_no_entities_key(self):
        Map.write(self.path, 1, 1, {}, set())
        self.assertNotIn("entities", json.loads(self.path.read_text()))
        self.assertEqual(Map.read_entities(self.path), {})

    def test_invalid_entities_are_rejected(self):
        for entries in (
            {"type": "goomba"},
            [{"type": "goomba", "x": 9, "y": 0}],
            [{"type": 3, "x": 0, "y": 0}],
            [{"type": "goomba", "x": 0, "y": 0}, {"type": "koopa", "x": 0, "y": 0}],
        ):
            with self.assertRaises(ValueError, msg=entries):
                Map.decode_entities(entries, 2, 2)

    def test_the_game_reads_the_entities_saved_by_the_editor(self):
        model = MapEditorModel(3, 2)
        model.set_entity((1, 1), "koopa")
        model.save(self.path)
        game_map = GameMap(pygame.Surface((16, 16)), {}, json.loads(self.path.read_text()))
        self.assertEqual([(e.type, e.column, e.row) for e in game_map.entities], [("koopa", 1, 1)])

    def test_place_undo_redo_and_unique_start(self):
        model = MapEditorModel(5, 5)
        model.set_entity((0, 0), "start", unique=True)
        model.set_entity((1, 0), "goomba")
        model.set_entity((4, 4), "start", unique=True)
        self.assertEqual(model.entities, {(1, 0): "goomba", (4, 4): "start"})
        model.undo()
        self.assertEqual(model.entities, {(0, 0): "start", (1, 0): "goomba"})
        model.redo()
        self.assertEqual(model.entities, {(1, 0): "goomba", (4, 4): "start"})
        model.resize(3, 3)
        self.assertEqual(model.entities, {(1, 0): "goomba"})

    def test_copy_rotate_and_paste_entities(self):
        model = MapEditorModel(6, 6, {(0, 0): Tile(0, 0)})
        model.set_entity((1, 0), "goomba")
        model.set_entity((0, 1), "start", unique=True)
        clipboard = model.copy((0, 0, 1, 1))
        self.assertEqual(clipboard.entities, {(1, 0): "goomba", (0, 1): "start"})
        self.assertEqual(set(clipboard.rotated().entities.values()), {"goomba", "start"})
        model.paste(clipboard, (3, 3), unique_entities={"start"})
        self.assertEqual(model.entities, {(1, 0): "goomba", (4, 3): "goomba", (3, 4): "start"})
        self.assertTrue(model.clear((3, 3, 4, 4)))
        self.assertEqual(model.entities, {(1, 0): "goomba"})

    def test_entities_mode_in_the_application(self):
        app = MapEditorApplication(self.path, LEVEL_SHEET, window_size=(1280, 720))
        app.step([Event(pygame.KEYDOWN, key=pygame.K_e, mod=0, unicode="")], 0.016)
        self.assertIs(app.state.mode, Mode.ENTITIES)

        palette = app.sidebar_view.palette_rect
        goomba = [entity.id for entity in app.state.entity_types].index("goomba")
        row = (palette.x + 10, palette.y + goomba * 36 + 10)
        center = app.camera.map_rect().center
        app.step([Event(pygame.MOUSEBUTTONDOWN, pos=row, button=1),
                  Event(pygame.MOUSEBUTTONUP, pos=row, button=1)], 0.016)
        self.assertEqual(app.state.selected_entity.id, "goomba")
        app.step([Event(pygame.MOUSEBUTTONDOWN, pos=center, button=1),
                  Event(pygame.MOUSEBUTTONUP, pos=center, button=1)], 0.016)
        self.assertEqual(list(app.model.entities.values()), ["goomba"])
        self.assertEqual(app.model.tiles, {}, "no tile is painted in the entities mode")
        app.render()

        app.state.select_entity(0)
        app.step([Event(pygame.MOUSEBUTTONDOWN, pos=center, button=2),
                  Event(pygame.MOUSEBUTTONUP, pos=center, button=2)], 0.016)
        self.assertEqual(app.state.selected_entity.id, "goomba", "middle click picks the entity")
        app.step([Event(pygame.MOUSEBUTTONDOWN, pos=center, button=3),
                  Event(pygame.MOUSEBUTTONUP, pos=center, button=3)], 0.016)
        self.assertEqual(app.model.entities, {})
        app.step([Event(pygame.KEYDOWN, key=pygame.K_e, mod=0, unicode="")], 0.016)
        self.assertIs(app.state.mode, Mode.TILES)
