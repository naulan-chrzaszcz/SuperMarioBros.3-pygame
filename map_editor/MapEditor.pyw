"""
A tile-based map editor for SuperMarioBros3.

Double-click this file (or run it without arguments) to open the launcher, or
open a map directly:
    python map_editor/MapEditor.pyw <map_path> [--sheet SHEET] [--size WIDTHxHEIGHT]
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pygame
import yaml

from map_editor.map_editor_cli import MapEditorCLI
from map_editor.src.application import MapEditorApplication
from map_editor.src.launcher import MapEditorLauncher

OPEN_ERRORS = (OSError, ValueError, pygame.error, yaml.YAMLError)


def run_launcher() -> int:
    """Shows the launcher, then the editor, and the launcher again when the
    editor is left with Esc. The clipboard is kept from one map to another."""
    clipboard = None
    message = None
    while True:
        request = MapEditorLauncher(message=message).run()
        if request is None:
            return 0
        try:
            application = MapEditorApplication(
                request.map_path, request.sheet_path, request.size, clipboard=clipboard
            )
        except OPEN_ERRORS as error:
            message = f"Cannot open {request.map_path.name}: {error}"
            continue
        message = None
        application.run()
        clipboard = application.state.clipboard
        if application.controller.window_closed:
            return 0


def run_editor(cli: MapEditorCLI) -> int:
    try:
        application = MapEditorApplication(cli.map_path, cli.sheet_path, cli.size)
    except OPEN_ERRORS as error:
        print(f"Cannot open the map editor: {error}", file=sys.stderr)
        return 1
    application.run()
    return 0


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)
    cli = MapEditorCLI.from_args(argv) if argv else None
    pygame.init()
    pygame.key.set_repeat(250, 35)
    try:
        return run_editor(cli) if cli else run_launcher()
    finally:
        pygame.quit()


if __name__ == "__main__":
    sys.exit(main())
