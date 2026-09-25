"""
A tile-based map editor for SuperMarioBros3.

Usage:
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


def main(argv=None) -> int:
    cli = MapEditorCLI.from_args(argv)
    pygame.init()
    pygame.key.set_repeat(250, 35)
    try:
        application = MapEditorApplication(cli.map_path, cli.sheet_path, cli.size)
    except (OSError, ValueError, yaml.YAMLError) as error:
        print(f"Cannot open the map editor: {error}", file=sys.stderr)
        pygame.quit()
        return 1
    application.run()
    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
