"""The entity types declared in ``res/entities.yaml``.

The map editor reads the same file to show them in its palette, so this module
only holds data and does not need a display.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple

import yaml
from pygame import PixelArray, Surface

from ..constants import PROJECT_ROOT

ENTITIES_FILE = PROJECT_ROOT / "res" / "entities.yaml"

Color = Tuple[int, int, int]
Palette = Tuple[Tuple[Color, Color], ...]


@dataclass(frozen=True)
class EntityType:
    id: str
    name: str
    image: str
    frame: Tuple[int, int, int, int]
    flip: bool = False
    palette: Palette = ()
    unique: bool = False
    description: str = ""


def load_entity_types(path: Path = ENTITIES_FILE) -> Dict[str, EntityType]:
    with Path(path).open(encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}
    types: Dict[str, EntityType] = {}
    for entry in data.get("entities", []):
        palette = tuple(
            (tuple(source), tuple(target)) for source, target in entry.get("palette", [])
        )
        types[entry["id"]] = EntityType(
            id=str(entry["id"]),
            name=str(entry.get("name", entry["id"])),
            image=str(entry["image"]),
            frame=tuple(entry["frame"]),
            flip=bool(entry.get("flip", False)),
            palette=palette,
            unique=bool(entry.get("unique", False)),
            description=str(entry.get("description", "")),
        )
    return types


_types: Optional[Dict[str, EntityType]] = None


def entity_types() -> Dict[str, EntityType]:
    """The types of ``res/entities.yaml``, read once."""
    global _types
    if _types is None:
        _types = load_entity_types()
    return _types


def recolored(surface: Surface, palette: Palette) -> Surface:
    """A copy of ``surface`` with the colors of ``palette`` swapped."""
    if not palette:
        return surface
    surface = surface.copy()
    pixels = PixelArray(surface)
    for source, target in palette:
        pixels.replace(source, target)
    pixels.close()
    return surface
