import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence, Tuple

from .src.constantes import DEFAULT_MAP_SIZE, DEFAULT_SHEET

SIZE_PATTERN = re.compile(r"^(\d+)[xX](\d+)$")


def parse_size(value: str) -> Tuple[int, int]:
    match = SIZE_PATTERN.fullmatch(value)
    if match is None:
        raise argparse.ArgumentTypeError("expected WIDTHxHEIGHT in tiles, e.g. 100x15")
    columns, rows = int(match.group(1)), int(match.group(2))
    if columns <= 0 or rows <= 0:
        raise argparse.ArgumentTypeError("the map size must be positive")
    return columns, rows


@dataclass
class MapEditorCLI:
    map_path: Path
    sheet_path: Path
    size: Optional[Tuple[int, int]]

    @classmethod
    def from_args(cls, argv: Optional[Sequence[str]] = None) -> "MapEditorCLI":
        default_columns, default_rows = DEFAULT_MAP_SIZE
        parser = argparse.ArgumentParser(
            description="SuperMarioBros3 tile map editor",
            epilog=(
                "examples:\n"
                "  %(prog)s res/maps/level_1.json --size 100x15\n"
                "  %(prog)s res/maps/stage_menu.json --sheet res/sheets/choice_menu_stage.png"
            ),
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        parser.add_argument(
            "map_path",
            type=Path,
            help="JSON map to edit; it is created on the first save if it does not exist",
        )
        parser.add_argument(
            "--sheet",
            dest="sheet_path",
            type=Path,
            default=DEFAULT_SHEET,
            help="tileset image (default: res/sheets/level.png)",
        )
        parser.add_argument(
            "--size",
            type=parse_size,
            help=(
                "map size in tiles, WIDTHxHEIGHT; defaults to the size of the existing "
                f"map, or {default_columns}x{default_rows} (one game screen) for a new "
                "map; resizes an existing map"
            ),
        )
        args = parser.parse_args(argv)
        if not args.sheet_path.is_file():
            parser.error(f"tileset not found: {args.sheet_path}")
        return cls(args.map_path, args.sheet_path, args.size)
