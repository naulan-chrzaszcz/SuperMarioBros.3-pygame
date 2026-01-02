from dataclasses import dataclass
from pathlib import Path

import argparse


@dataclass
class MapEditorCLI:
    map_width : int
    map_height: int
    sheet_path: Path
    map_name: Path

    @classmethod
    def from_args(cls):
        parser = argparse.ArgumentParser(description="A simple map editor")
        parser.add_argument(
            "map_width",
            type=int,
            help="Width is determined by a multiplier of tile size (16)"
        )
        parser.add_argument(
            "map_height",
            type=int,
            help="Height is determined by a multiplier of tile size (16)",
        )
        parser.add_argument(
            "sheet_path",
            type=Path,
            help="Path to the sheet file"
        )
        parser.add_argument(
            "map_name",
            type=Path,
            help="Path to write the map file"
        )
        args = parser.parse_args()

        if not args.sheet_path.is_file():
            parser.error(f"Tileset not found: {args.sheet_path}")
        return cls(**vars(args))

