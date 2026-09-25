"""
A tile-based map editor for SuperMarioBros3.

Usage:
    python map_editor/MapEditor.pyw <map_width> <map_height> <sheet_path> <map_name>
"""

import sys
from pathlib import Path

import pygame

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from map_editor.map_editor_cli import MapEditorCLI
from map_editor.src.commands_surface import CommandsSurface
from map_editor.src.constantes import TILE_SIZE
from map_editor.src.controllers import ApplicationController, MapEditorController
from map_editor.src.models import MapEditorModel
from map_editor.src.outputs.map import Map
from map_editor.src.tile_selection_surface import TileSelectionSurface
from map_editor.src.views import ApplicationView, MapEditorView

PANEL_GAP = 10
FRAMERATE_LIMIT = 60
MAP_VIEW_SIZE = (1280, 720)
MIN_SIDEBAR_WIDTH = 260
TILE_SELECTION_SCALE = 2
COMMANDS_HEIGHT = 180
WINDOW_TITLE = "SuperMarioBros3 - Map editor"


def main() -> None:
    cli = MapEditorCLI.from_args()

    pygame.init()
    sheet = pygame.image.load(cli.sheet_path)

    map_model = MapEditorModel(
        cli.map_width * TILE_SIZE,
        cli.map_height * TILE_SIZE,
        sheet,
    )
    if cli.map_name.is_file():
        map_model.load(cli.map_name)

    map_view = MapEditorView(
        (cli.map_width * TILE_SIZE, cli.map_height * TILE_SIZE),
        MAP_VIEW_SIZE,
    )
    sidebar_width = max(
        MIN_SIDEBAR_WIDTH,
        sheet.get_width() * TILE_SELECTION_SCALE + 2 * PANEL_GAP,
    )
    commands = CommandsSurface(sidebar_width - 2 * PANEL_GAP, COMMANDS_HEIGHT)
    tile_selection = TileSelectionSurface(sheet)
    application_view = ApplicationView(
        WINDOW_TITLE, map_view, commands, tile_selection, PANEL_GAP
    )
    map_controller = MapEditorController(
        map_model, map_view, commands, tile_selection
    )

    def export_map() -> None:
        Map.write(
            cli.map_name,
            map_model.tiles,
            map_model.collidables,
            map_model.width,
            map_model.height,
        )
        map_model.dirty = False
        print(f"Map saved to {cli.map_name}")

    commands.export_btn.on_click = export_map
    application = ApplicationController(
        application_view, map_controller, commands, tile_selection, export_map
    )

    clock = pygame.time.Clock()
    while application.running:
        clock.tick(FRAMERATE_LIMIT)
        for event in pygame.event.get():
            application.handle_event(event)

        application_view.set_caption(
            f"{WINDOW_TITLE}{' *' if map_model.dirty else ''}"
        )
        map_controller.update()
        commands.draw()
        tile_selection.draw()
        application_view.draw()

    if map_model.dirty:
        print("Warning: the editor closed with unsaved changes", file=sys.stderr)
    pygame.quit()


if __name__ == "__main__":
    main()
