import json
import re
from pathlib import Path
from typing import Dict, Iterable, Optional, Set, Tuple

from ..constantes import PROJECT_ROOT
from .tile import Tile

Cell = Tuple[int, int]


class Map:
    """Reads and writes the JSON map format loaded by ``src/inputs/map.py``."""

    EMPTY_TILE = "-1,-1"
    TILE_COORD_SEPARATOR = ","
    TILE_FRAMES_SEPARATOR = "+"
    TILE_ROTATION_SEPARATOR = "&"
    TILE_PATTERN = re.compile(
        r"^(?P<x>-?\d+)(?:\+(?P<x_frames>\d+))?,"
        r"(?P<y>-?\d+)(?:\+(?P<y_frames>\d+))?"
        r"(?:&(?P<rotation>[0-3]))?$"
    )

    @classmethod
    def decode_tile(cls, value: str) -> Optional[Tile]:
        if not isinstance(value, str):
            raise ValueError("Tile entries must be strings")

        match = cls.TILE_PATTERN.fullmatch(value)
        if match is None:
            raise ValueError(f"Invalid tile entry: {value!r}")

        x = int(match.group("x"))
        y = int(match.group("y"))
        if (x, y) == (-1, -1):
            if value != cls.EMPTY_TILE:
                raise ValueError(f"Empty tiles must use the exact value {cls.EMPTY_TILE!r}")
            return None
        if x < 0 or y < 0:
            raise ValueError(f"Tile coordinates cannot be negative: {value!r}")

        x_frames = int(match.group("x_frames") or 1)
        y_frames = int(match.group("y_frames") or 1)
        if x_frames < 1 or y_frames < 1:
            raise ValueError(f"Animation frame counts must be positive: {value!r}")
        if x_frames > 1 and y_frames > 1:
            raise ValueError(f"A tile can animate on only one axis: {value!r}")

        return Tile(x, y, x_frames, y_frames, int(match.group("rotation") or 0) * 90)

    @classmethod
    def encode_tile(cls, tile: Tile) -> str:
        if tile.x < 0 or tile.y < 0:
            raise ValueError("Tile coordinates cannot be negative")
        if tile.x_frames < 1 or tile.y_frames < 1:
            raise ValueError("Animation frame counts must be positive")
        if tile.x_frames > 1 and tile.y_frames > 1:
            raise ValueError("A tile can animate on only one axis")
        if tile.rotation not in (0, 90, 180, 270):
            raise ValueError("Tile rotation must be 0, 90, 180, or 270 degrees")

        tile_data = str(tile.x)
        if tile.x_frames > 1:
            tile_data += f"{cls.TILE_FRAMES_SEPARATOR}{tile.x_frames}"
        tile_data += f"{cls.TILE_COORD_SEPARATOR}{tile.y}"
        if tile.y_frames > 1:
            tile_data += f"{cls.TILE_FRAMES_SEPARATOR}{tile.y_frames}"
        if tile.rotation:
            tile_data += f"{cls.TILE_ROTATION_SEPARATOR}{tile.rotation // 90}"
        return tile_data

    @classmethod
    def read(cls, path: Path) -> Tuple[int, int, Dict[Cell, Tile], Set[Cell]]:
        """Returns ``(columns, rows, tiles, collidables)``, cells being ``(col, row)``."""
        with Path(path).open(encoding="utf-8") as file:
            map_data = json.load(file)

        if not isinstance(map_data, dict):
            raise ValueError("Map data must be a JSON object")
        tile_rows = map_data.get("tiles")
        collidable_rows = map_data.get("collidables")
        if not isinstance(tile_rows, list) or not tile_rows:
            raise ValueError("Map 'tiles' must be a non-empty matrix")
        if not isinstance(collidable_rows, list) or len(collidable_rows) != len(tile_rows):
            raise ValueError("Map 'collidables' must have the same rows as 'tiles'")
        if not isinstance(tile_rows[0], list) or not tile_rows[0]:
            raise ValueError("Map rows cannot be empty")

        columns = len(tile_rows[0])
        tiles: Dict[Cell, Tile] = {}
        collidables: Set[Cell] = set()
        for row, (tile_row, collidable_row) in enumerate(zip(tile_rows, collidable_rows)):
            if not isinstance(tile_row, list) or len(tile_row) != columns:
                raise ValueError(f"Tile row {row} has an invalid width")
            if not isinstance(collidable_row, list) or len(collidable_row) != columns:
                raise ValueError(f"Collidable row {row} has an invalid width")
            for col, (tile_data, collidable) in enumerate(zip(tile_row, collidable_row)):
                tile = cls.decode_tile(tile_data)
                if tile is not None:
                    tiles[(col, row)] = tile
                if not isinstance(collidable, bool):
                    raise ValueError(f"Collidable row {row} must contain only booleans")
                if collidable:
                    collidables.add((col, row))
        return columns, len(tile_rows), tiles, collidables

    @classmethod
    def read_entities(cls, path: Path) -> Dict[Cell, str]:
        """The entities placed on the map: ``{(col, row): type}``."""
        with Path(path).open(encoding="utf-8") as file:
            map_data = json.load(file)
        tile_rows = map_data.get("tiles") if isinstance(map_data, dict) else None
        if not isinstance(tile_rows, list) or not tile_rows or not isinstance(tile_rows[0], list):
            raise ValueError("Map 'tiles' must be a non-empty matrix")
        return cls.decode_entities(map_data.get("entities"), len(tile_rows[0]), len(tile_rows))

    @classmethod
    def decode_entities(cls, entries, columns: int, rows: int) -> Dict[Cell, str]:
        if entries is None:
            return {}
        if not isinstance(entries, list):
            raise ValueError("Map 'entities' must be a list")
        entities: Dict[Cell, str] = {}
        for entry in entries:
            if not isinstance(entry, dict) or not isinstance(entry.get("type"), str) or not entry["type"]:
                raise ValueError(f"Invalid entity: {entry!r}")
            col, row = entry.get("x"), entry.get("y")
            if type(col) is not int or type(row) is not int:
                raise ValueError(f"Entity {entry['type']!r} has invalid coordinates")
            cls._check_cell(col, row, columns, rows)
            if (col, row) in entities:
                raise ValueError(f"Two entities are on the cell {(col, row)}")
            entities[(col, row)] = entry["type"]
        return entities

    @classmethod
    def write(
        cls,
        path: Path,
        columns: int,
        rows: int,
        tiles: Dict[Cell, Tile],
        collidables: Iterable[Cell],
        sheet: Optional[Path] = None,
        entities: Optional[Dict[Cell, str]] = None,
        level: Optional[Dict] = None,
    ) -> None:
        """Writes the map. ``sheet`` is the tileset the map is drawn with: the game
        uses it to know which image the tile coordinates refer to. ``entities``
        are the enemies and items placed on it (see ``res/entities.yaml``) and
        ``level`` its settings (time limit, sky, music)."""
        if columns <= 0 or rows <= 0:
            raise ValueError("Map dimensions must be positive")

        map_data = {
            "tiles": [[cls.EMPTY_TILE] * columns for _ in range(rows)],
            "collidables": [[False] * columns for _ in range(rows)],
        }
        for (col, row), tile in tiles.items():
            cls._check_cell(col, row, columns, rows)
            map_data["tiles"][row][col] = cls.encode_tile(tile)
        for col, row in collidables:
            cls._check_cell(col, row, columns, rows)
            map_data["collidables"][row][col] = True
        if sheet is not None:
            map_data["sheet"] = cls.sheet_reference(sheet)
        if entities:
            for col, row in entities:
                cls._check_cell(col, row, columns, rows)
            map_data["entities"] = [
                {"type": kind, "x": col, "y": row}
                for (col, row), kind in sorted(entities.items(), key=lambda item: (item[0][1], item[0][0]))
            ]
        if level:
            map_data["level"] = dict(level)

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = path.with_name(f"{path.name}.tmp")
        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(map_data, file, separators=(",", ":"))
        temporary_path.replace(path)

    @classmethod
    def read_level(cls, path: Path) -> Dict:
        """The ``"level"`` block of a map file (empty when it has none)."""
        with Path(path).open(encoding="utf-8") as file:
            map_data = json.load(file)
        level = map_data.get("level") if isinstance(map_data, dict) else None
        if level is None:
            return {}
        if not isinstance(level, dict):
            raise ValueError("Map 'level' must be a mapping")
        return level

    @classmethod
    def read_sheet(cls, path: Path) -> Optional[Path]:
        """The tileset recorded in a map file, None when the file does not name one."""
        with Path(path).open(encoding="utf-8") as file:
            map_data = json.load(file)
        sheet = map_data.get("sheet") if isinstance(map_data, dict) else None
        if not isinstance(sheet, str) or not sheet:
            return None
        return (PROJECT_ROOT / sheet).resolve()

    @staticmethod
    def sheet_reference(sheet: Path) -> str:
        """Path of a sheet as stored in a map: relative to the project when possible."""
        sheet = Path(sheet).resolve()
        try:
            return sheet.relative_to(PROJECT_ROOT).as_posix()
        except ValueError:
            return str(sheet)

    @staticmethod
    def _check_cell(col: int, row: int, columns: int, rows: int) -> None:
        if not 0 <= col < columns or not 0 <= row < rows:
            raise ValueError(f"Cell is outside the map: {(col, row)}")
