from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterator, Optional, Tuple

import pygame
import yaml

from ..constantes import DEFAULT_COLOR_KEY, RESSOURCES_FILE, TILE_SIZE

SheetCell = Tuple[int, int]


@dataclass
class Tileset:
    """A sheet image and the tile names declared in its YAML metadata.

    The game resolves every placed tile through this metadata, so a tile that is
    not declared there cannot be loaded by the game.
    """

    image: pygame.Surface
    names: Dict[SheetCell, str] = field(default_factory=dict)
    metadata_path: Optional[Path] = None

    @property
    def columns(self) -> int:
        return self.image.get_width() // TILE_SIZE

    @property
    def rows(self) -> int:
        return self.image.get_height() // TILE_SIZE

    @property
    def has_metadata(self) -> bool:
        return self.metadata_path is not None

    def contains(self, x: int, y: int) -> bool:
        return 0 <= x < self.columns and 0 <= y < self.rows

    def name_of(self, x: int, y: int) -> Optional[str]:
        return self.names.get((x, y))

    def is_declared(self, x: int, y: int) -> bool:
        return self.contains(x, y) and (not self.has_metadata or (x, y) in self.names)

    def declared_cells(self) -> Iterator[SheetCell]:
        """Usable sheet cells in reading order."""
        for y in range(self.rows):
            for x in range(self.columns):
                if self.is_declared(x, y):
                    yield x, y

    @classmethod
    def load(cls, sheet_path: Path, ressources_file: Path = RESSOURCES_FILE) -> "Tileset":
        """Loads a sheet with the color key and metadata used by the game.

        Settings come from the matching ``ressources.yaml`` image entry, and fall
        back to a ``<sheet>.yaml`` file next to the image.
        """
        sheet_path = Path(sheet_path).resolve()
        color_key = DEFAULT_COLOR_KEY
        metadata_path = None

        entry = cls._find_ressource_entry(sheet_path, Path(ressources_file))
        if entry is not None:
            key = entry.get("colorKey")
            color_key = (key["r"], key["g"], key["b"]) if key else None
            if entry.get("metadata"):
                metadata_path = (Path(ressources_file).parent / entry["metadata"]).resolve()
        if metadata_path is None and sheet_path.with_suffix(".yaml").is_file():
            metadata_path = sheet_path.with_suffix(".yaml")

        image = pygame.image.load(sheet_path)
        if color_key is not None:
            image.set_colorkey(color_key)
        names = cls._read_names(metadata_path) if metadata_path else {}
        return cls(image, names, metadata_path)

    @staticmethod
    def _find_ressource_entry(sheet_path: Path, ressources_file: Path) -> Optional[dict]:
        if not ressources_file.is_file():
            return None
        with ressources_file.open(encoding="utf-8") as file:
            ressources = yaml.safe_load(file) or {}
        for entry in ressources.get("images", []):
            if (ressources_file.parent / entry["path"]).resolve() == sheet_path:
                return entry
        return None

    @staticmethod
    def _read_names(metadata_path: Path) -> Dict[SheetCell, str]:
        with metadata_path.open(encoding="utf-8") as file:
            metadata = yaml.safe_load(file) or {}
        return {
            (int(tile["coordinate"]["x"]), int(tile["coordinate"]["y"])): str(tile["name"])
            for tile in metadata.get("tiles", [])
        }
