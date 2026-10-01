"""The maps of ``res/maps`` that can be played as platform levels.

A map made with the editor records its tileset in a ``"sheet"`` key. Older
maps do not: the first sheet whose metadata declares every tile of the map is
used instead.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import pygame
import yaml
from pygame import Surface, image

from .constants import PROJECT_ROOT, RESSOURCES_FILE
from .entities.spawner import validate_spawns
from .inputs.map import Map, MapData, TileBehaviour, tile_behaviours
from .inputs.ressources import Ressources

MAPS_DIRECTORY = PROJECT_ROOT / "res" / "maps"
SHEETS_DIRECTORY = PROJECT_ROOT / "res" / "sheets"
# Tried first for maps that do not name their tileset, as in the map editor.
DEFAULT_SHEET_NAME = "level.png"
DEFAULT_COLOR_KEY = (255, 174, 201)


@dataclass(frozen=True)
class LevelInfo:
    """A map file of ``res/maps`` and whether it can be played (``error``)."""

    name: str
    path: Path
    sheet_path: Optional[Path] = None
    size: Optional[Tuple[int, int]] = None
    # Why the level cannot be played, None when it can.
    error: Optional[str] = None
    # The name given in the map editor (level settings), else the file name.
    title: str = ""

    @property
    def playable(self) -> bool:
        return self.error is None


@dataclass(frozen=True)
class SheetInfo:
    """A tileset image with its tile names and tile behaviours."""

    path: Path
    color_key: Optional[Tuple[int, int, int]]
    metadata: Optional[Dict[str, str]]
    behaviours: Optional[Dict[str, TileBehaviour]] = None


class LevelCatalog:
    """The playable maps of ``res/maps``, each one matched with its tileset.

    A map names its tileset (``sheet``); otherwise the first tileset of
    ``res/sheets`` (``level.png`` first) that declares all its tiles is used.
    """

    def __init__(
        self,
        maps_directory: Path = MAPS_DIRECTORY,
        sheets_directory: Path = SHEETS_DIRECTORY,
        ressources_file: Path = RESSOURCES_FILE,
        excluded: Iterable[Path] = (),
        root: Path = PROJECT_ROOT,
    ):
        self.maps_directory = Path(maps_directory)
        self.sheets_directory = Path(sheets_directory)
        self.ressources_file = Path(ressources_file)
        self.root = Path(root)
        self.excluded = {Path(path).resolve() for path in excluded}
        self._levels: List[LevelInfo] = []
        self._sheets: Dict[Path, SheetInfo] = {}
        self._images: Dict[Path, Surface] = {}

    @property
    def levels(self) -> List[LevelInfo]:
        return list(self._levels)

    def refresh(self) -> List[LevelInfo]:
        """Scans the maps directory again (maps may have been edited)."""
        self._sheets = {}
        self._images = {}
        paths = sorted(self.maps_directory.glob("*.json")) if self.maps_directory.is_dir() else []
        self._levels = [self.info(path) for path in paths if path.resolve() not in self.excluded]
        return self.levels

    def find(self, name: str) -> Optional[LevelInfo]:
        """The level ``name`` (file name without ``.json``), None when there is none."""
        for level in self._levels:
            if level.name == name:
                return level
        path = self.maps_directory / f"{name}.json"
        if path.is_file() and path.resolve() not in self.excluded:
            return self.info(path)
        return None

    def info(self, path: Path, sheet_path: Optional[Path] = None) -> LevelInfo:
        """Describes a map file; ``sheet_path`` forces its tileset."""
        path = Path(path)
        name = path.stem
        try:
            with path.open(encoding="utf-8") as file:
                data = json.load(file)
            parsed = MapData.parse(data)
            size = (parsed.columns, parsed.rows)
            validate_spawns(parsed.entities)
            title = parsed.settings.name or name
            result = self._check_sheet(data, name, path, size, parsed, sheet_path)
        except (OSError, ValueError, TypeError, IndexError, KeyError, yaml.YAMLError, pygame.error) as error:
            return LevelInfo(name, path, error=f"Cannot read the map: {error}", title=name)
        return LevelInfo(result.name, result.path, result.sheet_path, result.size, result.error, title)

    def _check_sheet(self, data, name, path, size, parsed, sheet_path) -> LevelInfo:
        if sheet_path is None and isinstance(data.get("sheet"), str):
            sheet_path = self.root / data["sheet"]
        if sheet_path is not None:
            sheet_path = Path(sheet_path).resolve()
            if not sheet_path.is_file():
                return LevelInfo(name, path, size=size, error=f"Missing tileset {sheet_path.name}")
            sheet = self.sheet(sheet_path)
            if sheet.metadata is None:
                return LevelInfo(name, path, sheet_path, size, f"{sheet_path.name} has no metadata")
            try:
                self._validate_sheet(parsed, sheet)
            except ValueError as error:
                return LevelInfo(name, path, sheet_path, size, str(error))
            return LevelInfo(name, path, sheet_path, size)

        for candidate in self._sheet_paths():
            sheet = self.sheet(candidate)
            if sheet.metadata is not None:
                try:
                    self._validate_sheet(parsed, sheet)
                except ValueError:
                    continue
                return LevelInfo(name, path, candidate, size)
        return LevelInfo(name, path, size=size, error="No tileset declares every tile of this map")

    @staticmethod
    def _validate_sheet(parsed: MapData, sheet: SheetInfo) -> None:
        if sheet.metadata is None:
            raise ValueError(f"{sheet.path.name} has no metadata")
        parsed.validate_sheet(
            sheet.metadata, tile_behaviours(sheet.metadata, sheet.behaviours),
            image.load(str(sheet.path)).get_size(),
        )

    def load(self, level: LevelInfo) -> Map:
        """Builds the map of a playable level. Raises ValueError otherwise."""
        if not level.playable:
            raise ValueError(level.error)
        sheet = self.sheet(level.sheet_path)
        with level.path.open(encoding="utf-8") as file:
            data = json.load(file)
        return Map(self._image(sheet), sheet.metadata, data, sheet.behaviours)

    def sheet(self, path: Path) -> SheetInfo:
        path = Path(path).resolve()
        if path not in self._sheets:
            self._sheets[path] = self._read_sheet(path)
        return self._sheets[path]

    def _image(self, sheet: SheetInfo) -> Surface:
        if sheet.path not in self._images:
            surface = image.load(str(sheet.path)).convert()
            if sheet.color_key is not None:
                surface.set_colorkey(sheet.color_key)
            self._images[sheet.path] = surface
        return self._images[sheet.path]

    def _sheet_paths(self) -> List[Path]:
        if not self.sheets_directory.is_dir():
            return []
        paths = sorted(path.resolve() for path in self.sheets_directory.glob("*.png"))
        return sorted(paths, key=lambda path: path.name != DEFAULT_SHEET_NAME)

    def _read_sheet(self, path: Path) -> SheetInfo:
        """Color key and tile names, from ``ressources.yaml`` or ``<sheet>.yaml``."""
        color_key = DEFAULT_COLOR_KEY
        metadata_path = None
        for entry in self._ressource_images():
            if (self.root / entry.get("path", "")).resolve() == path:
                key = entry.get("colorKey")
                color_key = (key["r"], key["g"], key["b"]) if key else None
                if entry.get("metadata"):
                    metadata_path = self.root / entry["metadata"]
                break
        if metadata_path is None and path.with_suffix(".yaml").is_file():
            metadata_path = path.with_suffix(".yaml")
        metadata = behaviours = None
        if metadata_path is not None:
            metadata = Ressources.read_metadata(metadata_path)
            behaviours = Ressources.read_behaviours(metadata_path)
        return SheetInfo(path, color_key, metadata, behaviours)

    def _ressource_images(self) -> List[dict]:
        with self.ressources_file.open(encoding="utf-8") as file:
            return (yaml.safe_load(file) or {}).get("images", [])
