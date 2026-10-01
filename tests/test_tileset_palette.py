"""YAML-driven tile palette and existing map compatibility."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from map_editor.src.application import MapEditorApplication
from map_editor.src.constants import DEFAULT_SHEET, SHEETS_DIRECTORY
from map_editor.src.controllers.sidebar_controller import SidebarController
from map_editor.src.models.editor_state import EditorState
from map_editor.src.models.map_editor_model import MapEditorModel
from map_editor.src.models.tileset import Tileset
from map_editor.src.outputs.tile import Tile
from src.inputs.map import Map
from src.inputs.ressources import Ressources
from src.levels import LevelCatalog


class TilesetPaletteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((32, 32))

    @classmethod
    def tearDownClass(cls) -> None:
        pygame.quit()

    def test_named_noncontiguous_animation_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            sheet = Path(folder) / "sheet.png"
            image = pygame.Surface((64, 16))
            image.fill((200, 0, 0), (0, 0, 16, 16))
            image.fill((0, 0, 200), (48, 0, 16, 16))
            pygame.image.save(image, str(sheet))
            sheet.with_suffix(".yaml").write_text(
                "tiles:\n"
                "  - name: coin_frame_0\n    coordinate: {x: 0, y: 0}\n"
                "  - name: wall\n    coordinate: {x: 1, y: 0}\n"
                "  - name: coin_frame_1\n    coordinate: {x: 3, y: 0}\n"
            )
            tileset = Tileset.load(sheet, Path(folder) / "missing.yaml")
            state = EditorState(tileset, entity_types=())
            self.assertEqual(list(tileset.palette_cells()), [(0, 0), (1, 0)])
            self.assertEqual(tileset.animations[(0, 0)], ((0, 0), (3, 0)))
            self.assertEqual(state.selected_tile(), Tile(0, 0, 1, 1, 0))
            state.cycle_selection(1)
            self.assertEqual(state.selected_tile(), Tile(1, 0, 1, 1, 0))
            state.select(3, 0)
            self.assertEqual(state.selected_tile(), Tile(0, 0, 1, 1, 0))
            output = Path(folder) / "map.json"
            model = MapEditorModel(1, 1, {(0, 0): state.selected_tile()})
            model.save(output, sheet)
            self.assertEqual(json.loads(output.read_text())["tiles"], [["0,0"]])
            parsed = Map(
                tileset.image, Ressources.read_metadata(sheet.with_suffix(".yaml")),
                json.loads(output.read_text()), animations=tileset.animations,
            )
            animated = parsed.tile_at(0, 0)
            self.assertEqual([frame.get_at((0, 0))[:3] for frame in animated.animation.frames],
                             [(200, 0, 0), (0, 0, 200)])
            parsed.update(1 / parsed.ANIMATION_SPEED)
            self.assertEqual(animated.image.get_at((0, 0))[:3], (0, 0, 200))
            manifest = Path(folder) / "ressources.yaml"
            manifest.write_text(
                "images:\n"
                "  - id: sheet\n    path: sheet.png\n    metadata: sheet.yaml\n"
                "maps:\n"
                "  - id: test\n    path: map.json\n    sheet: sheet\n"
            )
            resources = Ressources.load(manifest, Path(folder))
            self.assertEqual(resources.load_map("test").animations, tileset.animations)
            catalog = LevelCatalog(
                maps_directory=Path(folder), sheets_directory=Path(folder),
                ressources_file=manifest, root=Path(folder),
            )
            level = catalog.info(output, sheet)
            self.assertTrue(level.playable, level.error)
            self.assertEqual(catalog.load(level).animations, tileset.animations)
            state.pick(Tile(3, 0, 1, 1, 90))
            self.assertEqual(state.selected_tile(), Tile(3, 0, 1, 1, 90))
            state.cycle_selection(1)
            self.assertEqual(state.selected_tile(), Tile(1, 0, 1, 1, 90))
            legacy = Map(
                tileset.image, Ressources.read_metadata(sheet.with_suffix(".yaml")),
                {"tiles": [["0+2,0"]], "collidables": [[False]]},
                animations=tileset.animations,
            )
            self.assertEqual(legacy.tile_at(0, 0).animation.frames[1].get_at((0, 0))[:3],
                             (0, 0, 0))

    def test_invalid_animation_is_reported_with_yaml_context(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            sheet = Path(folder) / "sheet.png"
            pygame.image.save(pygame.Surface((32, 16)), str(sheet))
            metadata = sheet.with_suffix(".yaml")
            for animation in (
                "{axis: x, frames: 3}", "{axis: diagonal, frames: 2}",
                "{axis: x, frames: true}", "{axis: x, frames: 2, speed: 3}",
            ):
                with self.subTest(animation=animation):
                    metadata.write_text(
                        "tiles:\n  - name: coin\n    coordinate: {x: 0, y: 0}\n"
                        f"    animation: {animation}\n"
                    )
                    with self.assertRaisesRegex(ValueError, "sheet.yaml.*coin.*animation"):
                        Tileset.load(sheet, Path(folder) / "missing.yaml")

    def test_metadata_free_sheet_still_selects_individual_cells(self) -> None:
        tileset = Tileset(pygame.Surface((32, 16)))
        state = EditorState(tileset, entity_types=())
        state.cycle_selection(1)
        self.assertEqual(state.selected_tile(), Tile(1, 0, 1, 1, 0))

    def test_vertical_animation_and_overlapping_strips(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            sheet = Path(folder) / "sheet.png"
            pygame.image.save(pygame.Surface((16, 48)), str(sheet))
            metadata = sheet.with_suffix(".yaml")
            metadata.write_text(
                "tiles:\n"
                "  - name: bush\n    coordinate: {x: 0, y: 0}\n"
                "    animation: {axis: y, frames: 3}\n"
            )
            tileset = Tileset.load(sheet, Path(folder) / "missing.yaml")
            state = EditorState(tileset, entity_types=())
            state.select(0, 2)
            self.assertEqual(state.selected_tile(), Tile(0, 0, 1, 1, 0))
            metadata.write_text(
                metadata.read_text() +
                "  - name: vine\n    coordinate: {x: 0, y: 1}\n"
                "    animation: {axis: y, frames: 2}\n"
            )
            with self.assertRaisesRegex(ValueError, "overlaps"):
                Tileset.load(sheet, Path(folder) / "missing.yaml")

    def test_bundled_tilesets_and_existing_map(self) -> None:
        level = Tileset.load(DEFAULT_SHEET)
        self.assertEqual(level.animations[(4, 3)], tuple((x, 3) for x in range(4, 9)))
        self.assertEqual(level.animations[(14, 0)], ((14, 0), (14, 1), (14, 2)))
        self.assertNotIn((5, 3), list(level.palette_cells()))
        stage = Tileset.load(SHEETS_DIRECTORY / "choice_menu_stage.png")
        self.assertEqual(stage.animations[(0, 2)], tuple((x, 2) for x in range(4)))
        data = json.loads((DEFAULT_SHEET.parent.parent / "maps" / "stage_menu.json").read_text())
        self.assertEqual(data["tiles"][0][0], "0+4,2")
        state = EditorState(stage, entity_types=())
        state.pick(Tile(0, 2, 4, 1, 0))
        self.assertEqual(state.selected_tile(), Tile(0, 2, 4, 1, 0))
        stage_map = Map(stage.image, {f"{x},{y}": name for (x, y), name in stage.names.items()}, data)
        self.assertEqual(stage_map.columns, len(data["tiles"][0]))

    def test_long_named_list_scrolls_to_selection_and_clicks_visible_row(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            app = MapEditorApplication(Path(folder) / "map.json", DEFAULT_SHEET, size=(2, 2))
            sidebar = app.sidebar_view
            cells = list(app.tileset.palette_cells())
            app.state.cycle_selection(60)
            app.step([], 0.016)
            self.assertGreater(sidebar.tile_scroll, 0)
            row = sidebar.tileset_rect.topleft
            expected = cells[sidebar.tile_scroll + 1]
            sidebar_click = pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": 1, "pos": (row[0] + 2, row[1] + 36 + 2)},
            )
            SidebarController(app.state, sidebar).handle_mouse(sidebar_click)
            self.assertEqual((app.state.selection_x, app.state.selection_y), expected)

    def test_sidebar_click_on_animation_frame_selects_origin(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            sheet = Path(folder) / "sheet.png"
            pygame.image.save(pygame.Surface((48, 16)), str(sheet))
            sheet.with_suffix(".yaml").write_text(
                "tiles:\n"
                "  - name: coin\n    coordinate: {x: 0, y: 0}\n"
                "    animation: {axis: x, frames: 3}\n"
            )
            app = MapEditorApplication(Path(folder) / "map.json", sheet, size=(2, 2))
            sidebar = app.sidebar_view
            app.step([], 0.016)
            self.assertGreaterEqual(sidebar.tileset_rect.height, 3 * 36)
            click = sidebar.tileset_rect.topleft
            mouse = pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": 1, "pos": (click[0] + 2, click[1] + 1)},
            )
            previous_message = app.state.message
            SidebarController(app.state, sidebar).handle_mouse(mouse)
            self.assertEqual(app.state.selected_tile(), Tile(0, 0, 1, 1, 0))
            self.assertEqual(app.state.message, previous_message)
            self.assertFalse(any("Frames X" in button.text for button in sidebar.buttons))

    def test_explicit_names_in_custom_order_and_invalid_references(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            sheet = Path(folder) / "sheet.png"
            pygame.image.save(pygame.Surface((48, 16)), str(sheet))
            metadata = sheet.with_suffix(".yaml")
            metadata.write_text(
                "tiles:\n"
                "  - name: first\n    coordinate: {x: 0, y: 0}\n"
                "    animation: {frames: [first, third, second]}\n"
                "  - name: second\n    coordinate: {x: 1, y: 0}\n"
                "  - name: third\n    coordinate: {x: 2, y: 0}\n"
            )
            tileset = Tileset.load(sheet, Path(folder) / "missing.yaml")
            self.assertEqual(tileset.animations[(0, 0)], ((0, 0), (2, 0), (1, 0)))
            self.assertEqual(list(tileset.palette_cells()), [(0, 0)])
            metadata.write_text(metadata.read_text().replace("third, second", "missing, second"))
            with self.assertRaisesRegex(ValueError, "missing"):
                Tileset.load(sheet, Path(folder) / "missing.yaml")

    def test_named_frames_require_contiguous_indices_and_unique_coordinates(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            sheet = Path(folder) / "sheet.png"
            pygame.image.save(pygame.Surface((48, 16)), str(sheet))
            metadata = sheet.with_suffix(".yaml")
            metadata.write_text(
                "tiles:\n"
                "  - name: coin_frame_0\n    coordinate: {x: 0, y: 0}\n"
                "  - name: coin_frame_2\n    coordinate: {x: 2, y: 0}\n"
            )
            with self.assertRaisesRegex(ValueError, "missing frame indices"):
                Tileset.load(sheet, Path(folder) / "missing.yaml")
            metadata.write_text(metadata.read_text().replace("x: 2", "x: 0"))
            with self.assertRaisesRegex(ValueError, "share a coordinate"):
                Tileset.load(sheet, Path(folder) / "missing.yaml")
