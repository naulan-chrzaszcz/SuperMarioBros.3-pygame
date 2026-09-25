"""
A tile-based map editor for SuperMarioBros3.

Usage:
    python map_editor/MapEditor.pyw <map_width> <map_height> <sheet_path> <map_name>
"""

import sys
from pathlib import Path

import pygame
from pygame._sdl2 import Renderer, Texture, Window

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from map_editor.map_editor_cli import MapEditorCLI
from map_editor.src.commands_surface import CommandsSurface
from map_editor.src.constantes import TILE_SIZE
from map_editor.src.controllers import MapEditorController
from map_editor.src.models import MapEditorModel
from map_editor.src.outputs.map import Map
from map_editor.src.tile_selection_surface import TileSelectionSurface
from map_editor.src.views import MapEditorView

WINDOW_GAP = 10
FRAMERATE_LIMIT = 60
MAP_WINDOW_SIZE = (1280, 720)
COMMAND_WINDOW_SIZE = (200, 300)
WINDOW_TITLE = "SuperMarioBros3 - Map editor"


def main() -> None:
    cli = MapEditorCLI.from_args()

    pygame.init()
    sheet = pygame.image.load(cli.sheet_path)

    map_window = Window(title=WINDOW_TITLE, size=MAP_WINDOW_SIZE)
    map_renderer = Renderer(map_window)
    map_model = MapEditorModel(
        cli.map_width * TILE_SIZE,
        cli.map_height * TILE_SIZE,
        sheet,
    )
    if cli.map_name.is_file():
        map_model.load(cli.map_name)

    map_view = MapEditorView(
        (cli.map_width * TILE_SIZE, cli.map_height * TILE_SIZE)
    )

    cmd_window = Window(
        title=f"{WINDOW_TITLE} - settings",
        size=COMMAND_WINDOW_SIZE,
        borderless=True,
    )
    cmd_renderer = Renderer(cmd_window)
    cmd_surface = CommandsSurface(*COMMAND_WINDOW_SIZE)

    sheet_window = Window(
        title=f"{WINDOW_TITLE} - tile selector",
        size=sheet.get_size(),
        borderless=True,
    )
    sheet_renderer = Renderer(sheet_window)
    tile_selection_surface = TileSelectionSurface(sheet)
    _update_frame_limits(cmd_surface, tile_selection_surface, sheet)

    map_controller = MapEditorController(
        map_model,
        map_view,
        cmd_surface,
        tile_selection_surface,
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

    cmd_surface.export_btn.on_click = export_map

    map_window.show()
    cmd_window.show()
    sheet_window.show()

    clock = pygame.time.Clock()
    running = True
    while running:
        clock.tick(FRAMERATE_LIMIT)
        _position_windows(map_window, cmd_window, sheet_window)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.WINDOWCLOSE:
                running = False
                break

            event_window = getattr(event, "window", None)
            if event_window == map_window:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        break
                    if event.key == pygame.K_r:
                        cmd_surface.rotate()
                    if event.key == pygame.K_s and event.mod & pygame.KMOD_CTRL:
                        export_map()
                map_controller.handle_event(event)
            elif event_window == sheet_window:
                tile_selection_surface.handle_event(event)
                _update_frame_limits(cmd_surface, tile_selection_surface, sheet)
            elif event_window == cmd_window:
                cmd_surface.handle_event(event)

        map_window.title = f"{WINDOW_TITLE}{' *' if map_model.dirty else ''}"
        map_controller.update()
        cmd_surface.draw()
        tile_selection_surface.draw()

        _present(map_renderer, map_view)
        _present(cmd_renderer, cmd_surface)
        _present(sheet_renderer, tile_selection_surface)

    if map_model.dirty:
        print("Warning: the editor closed with unsaved changes", file=sys.stderr)
    map_window.destroy()
    cmd_window.destroy()
    sheet_window.destroy()
    pygame.quit()


def _position_windows(
    map_window: Window, cmd_window: Window, sheet_window: Window
) -> None:
    cmd_window.position = (
        map_window.position[0] + map_window.size[0] + WINDOW_GAP,
        map_window.position[1],
    )
    sheet_window.position = (
        cmd_window.position[0],
        cmd_window.position[1] + cmd_window.size[1] + WINDOW_GAP,
    )


def _update_frame_limits(
    commands: CommandsSurface,
    tile_selection: TileSelectionSurface,
    sheet: pygame.Surface,
) -> None:
    commands.set_frame_limits(
        sheet.get_width() // TILE_SIZE - tile_selection.selection_x,
        sheet.get_height() // TILE_SIZE - tile_selection.selection_y,
    )


def _present(renderer: Renderer, surface: pygame.Surface) -> None:
    texture = Texture.from_surface(renderer, surface)
    texture.draw(dstrect=(0, 0))
    renderer.present()


if __name__ == "__main__":
    main()
