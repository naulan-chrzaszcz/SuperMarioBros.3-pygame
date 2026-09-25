"""The entities of ``res/entities.yaml`` that can be placed on a map.

The game reads the same file (``src/entities/catalog.py``) and gives each type
its behaviour.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple

import yaml

from ..constantes import DEFAULT_COLOR_KEY, ENTITIES_FILE, PROJECT_ROOT, RESSOURCES_FILE

Color = Tuple[int, int, int]


@dataclass(frozen=True)
class EntityType:
    id: str
    name: str
    # Image of the entity in the palette: a frame of a sheet.
    sheet_path: Optional[Path]
    frame: Tuple[int, int, int, int]
    color_key: Optional[Color] = DEFAULT_COLOR_KEY
    flip: bool = False
    palette: Tuple[Tuple[Color, Color], ...] = ()
    unique: bool = False
    description: str = ""


def load_entity_types(
    path: Path = ENTITIES_FILE,
    ressources_file: Path = RESSOURCES_FILE,
    root: Path = PROJECT_ROOT,
) -> Tuple[EntityType, ...]:
    """The entity types in declaration order; none when the file is missing."""
    try:
        with Path(path).open(encoding="utf-8") as file:
            entries = (yaml.safe_load(file) or {}).get("entities", [])
    except (OSError, yaml.YAMLError):
        return ()
    images = _ressource_images(ressources_file)
    types = []
    for entry in entries:
        image = images.get(entry.get("image"), {})
        key = image.get("colorKey")
        types.append(EntityType(
            id=str(entry["id"]),
            name=str(entry.get("name", entry["id"])),
            sheet_path=(root / image["path"]) if image.get("path") else None,
            frame=tuple(entry.get("frame", (0, 0, 16, 16))),
            color_key=(key["r"], key["g"], key["b"]) if key else None,
            flip=bool(entry.get("flip", False)),
            palette=tuple((tuple(a), tuple(b)) for a, b in entry.get("palette", [])),
            unique=bool(entry.get("unique", False)),
            description=str(entry.get("description", "")),
        ))
    return tuple(types)


def _ressource_images(path: Path) -> Dict[str, dict]:
    try:
        with Path(path).open(encoding="utf-8") as file:
            entries = (yaml.safe_load(file) or {}).get("images", [])
    except (OSError, yaml.YAMLError):
        return {}
    return {entry["id"]: entry for entry in entries if "id" in entry}
