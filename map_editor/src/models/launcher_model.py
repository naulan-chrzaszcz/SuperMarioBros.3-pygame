"""Launcher data model for maps, tilesets and validated launch requests."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, FrozenSet, List, Optional, Tuple

from ..constants import (
    DEFAULT_MAP_SIZE,
    DEFAULT_SHEET,
    LAUNCHER_SETTINGS_FILE,
    MAPS_DIRECTORY,
    MAX_MAP_SIZE,
    PROJECT_ROOT,
    RESSOURCES_FILE,
    SHEETS_DIRECTORY,
)
from ..outputs.map import Map
from .editor_state import MessageLevel
from .map_editor_model import MapEditorModel
from .tileset import SheetCell, Tileset

MAP_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


@dataclass(frozen=True)
class MapEntry:
    """A map listed by the launcher, with readable metadata or an error."""

    path: Path
    size: Optional[Tuple[int, int]] = None
    sheet_cells: FrozenSet[SheetCell] = frozenset()
    error: Optional[str] = None
    # Tileset recorded in the map file by the editor.
    sheet: Optional[Path] = None

    @classmethod
    def read(cls, path: Path) -> "MapEntry":
        """Reads map metadata without preventing the launcher from listing bad files."""
        try:
            columns, rows, tiles, _ = Map.read(path)
            sheet = Map.read_sheet(path)
        except (OSError, ValueError) as error:
            return cls(path, error=str(error))
        cells = frozenset((tile.x, tile.y) for tile in tiles.values())
        return cls(path, (columns, rows), cells, sheet=sheet)


@dataclass(frozen=True)
class SheetEntry:
    """A tileset listed by the launcher, with optional declared tile names."""

    path: Path
    # Tile names from the metadata, None when the sheet has no metadata.
    names: Optional[Dict[SheetCell, str]] = None

    @property
    def has_metadata(self) -> bool:
        return self.names is not None

    @classmethod
    def read(cls, path: Path, ressources_file: Path) -> "SheetEntry":
        """Reads sheet metadata; invalid metadata leaves the sheet selectable."""
        _, metadata_path = Tileset.settings_of(path, ressources_file)
        if metadata_path is None:
            return cls(path)
        try:
            return cls(path, Tileset.read_names(metadata_path))
        except (OSError, ValueError, KeyError, TypeError):
            return cls(path)


@dataclass(frozen=True)
class LaunchRequest:
    """Validated map, tileset and optional resize chosen in the launcher."""

    map_path: Path
    sheet_path: Path
    # New size of the map, None to keep its size.
    size: Optional[Tuple[int, int]] = None


@dataclass
class LauncherModel:
    """Choice of the map to edit (an existing one or a new one) and its tileset."""

    maps_directory: Path = MAPS_DIRECTORY
    sheets_directory: Path = SHEETS_DIRECTORY
    settings_file: Path = LAUNCHER_SETTINGS_FILE
    ressources_file: Path = RESSOURCES_FILE
    maps: List[MapEntry] = field(default_factory=list)
    sheets: List[SheetEntry] = field(default_factory=list)
    # Index in ``maps``, None when a new map is being created.
    selected: Optional[int] = None
    sheet_index: int = 0
    name: str = ""
    width: str = ""
    height: str = ""
    message: str = ""
    message_level: MessageLevel = MessageLevel.INFO

    def __post_init__(self) -> None:
        self.settings = self._read_settings()
        self.refresh()
        last = self.settings.get("last_map")
        paths = [entry.path.name for entry in self.maps]
        if last in paths:
            self.select_map(paths.index(last))
        elif self.maps:
            self.select_map(0)
        else:
            self.select_new()

    @property
    def is_new(self) -> bool:
        return self.selected is None

    @property
    def sheet(self) -> Optional[SheetEntry]:
        return self.sheets[self.sheet_index] if self.sheets else None

    @property
    def selected_map(self) -> Optional[MapEntry]:
        return None if self.selected is None else self.maps[self.selected]

    def refresh(self) -> None:
        """Reloads available maps and sheets from disk."""
        self.maps = sorted(
            (MapEntry.read(path) for path in self.maps_directory.glob("*.json")),
            key=lambda entry: entry.path.name.lower(),
        )
        sheets = [SheetEntry.read(path, self.ressources_file) for path in self.sheets_directory.glob("*.png")]
        # Real tilesets (with metadata) first.
        self.sheets = sorted(sheets, key=lambda sheet: (not sheet.has_metadata, sheet.path.name.lower()))

    def select_new(self) -> None:
        """Switches the form to create a new map with default values."""
        self.selected = None
        self.name = ""
        self.width, self.height = (str(value) for value in DEFAULT_MAP_SIZE)
        self.sheet_index = self._sheet_index_of(DEFAULT_SHEET)
        self.message = ""

    def select_map(self, index: int) -> None:
        """Selects an existing map and fills the form from its metadata."""
        entry = self.maps[index]
        self.selected = index
        self.name = entry.path.stem
        self.width, self.height = (str(value) for value in entry.size) if entry.size else ("", "")
        self.sheet_index = self.guess_sheet(entry)
        if entry.error:
            self.notify(f"This map cannot be read: {entry.error}", MessageLevel.ERROR)
        else:
            self.message = ""

    def select_sheet(self, index: int) -> None:
        self.sheet_index = index

    def guess_sheet(self, entry: MapEntry) -> int:
        """The tileset recorded in the map, otherwise the one last used with this
        map, otherwise the first tileset that declares every tile of the map."""
        if entry.sheet is not None:
            for index, sheet in enumerate(self.sheets):
                if sheet.path.resolve() == entry.sheet:
                    return index
        remembered = self.settings.get("sheets", {}).get(entry.path.name)
        if remembered:
            index = self._sheet_index_of(PROJECT_ROOT / remembered)
            if self.sheets and self.sheets[index].path.resolve() == (PROJECT_ROOT / remembered).resolve():
                return index
        if entry.sheet_cells:
            for index, sheet in enumerate(self.sheets):
                if sheet.has_metadata and entry.sheet_cells <= sheet.names.keys():
                    return index
        return self._sheet_index_of(DEFAULT_SHEET)

    def notify(self, message: str, level: MessageLevel = MessageLevel.INFO) -> None:
        """Stores a launcher status message for the view."""
        self.message = message
        self.message_level = level

    def size(self) -> Tuple[int, int]:
        """Parses and validates the map size fields."""
        try:
            columns, rows = int(self.width), int(self.height)
        except ValueError:
            raise ValueError("Enter the map width and height in tiles") from None
        if not (0 < columns <= MAX_MAP_SIZE and 0 < rows <= MAX_MAP_SIZE):
            raise ValueError(f"The map size must be between 1 and {MAX_MAP_SIZE} tiles")
        return columns, rows

    @property
    def resizes(self) -> bool:
        entry = self.selected_map
        try:
            return entry is not None and entry.size is not None and self.size() != entry.size
        except ValueError:
            return False

    def request(self) -> LaunchRequest:
        """Validates the choices (creating the file of a new map) and returns what
        the editor must open. Raises ValueError with a readable message."""
        if self.sheet is None:
            raise ValueError(f"No tileset found in {self.sheets_directory}")
        entry = self.selected_map
        if entry is not None and entry.error:
            raise ValueError(f"This map cannot be read: {entry.error}")
        size = self.size()
        if self.is_new:
            if not MAP_NAME_PATTERN.fullmatch(self.name):
                raise ValueError("The map name can only contain letters, digits, - and _")
            map_path = self.maps_directory / f"{self.name}.json"
            if map_path.exists():
                raise ValueError(f"{map_path.name} already exists: select it in the list")
            self.maps_directory.mkdir(parents=True, exist_ok=True)
            MapEditorModel(*size).save(map_path, self.sheet.path)
            request = LaunchRequest(map_path, self.sheet.path)
        else:
            request = LaunchRequest(entry.path, self.sheet.path, size if self.resizes else None)
        self._remember(request)
        return request

    def _sheet_index_of(self, path: Path) -> int:
        for index, sheet in enumerate(self.sheets):
            if sheet.path.resolve() == Path(path).resolve():
                return index
        return 0

    def _read_settings(self) -> dict:
        try:
            settings = json.loads(self.settings_file.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}
        return settings if isinstance(settings, dict) else {}

    def _remember(self, request: LaunchRequest) -> None:
        try:
            sheet = request.sheet_path.resolve().relative_to(PROJECT_ROOT).as_posix()
        except ValueError:
            sheet = str(request.sheet_path.resolve())
        self.settings.setdefault("sheets", {})[request.map_path.name] = sheet
        self.settings["last_map"] = request.map_path.name
        try:
            self.settings_file.write_text(json.dumps(self.settings, indent=2), encoding="utf-8")
        except OSError:
            pass  # Remembering the choice is only a convenience.
