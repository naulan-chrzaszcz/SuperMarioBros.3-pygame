"""The entity types declared in ``res/entities.yaml``.

The map editor reads the same file to show them in its palette, so this module
only holds data and does not need a display.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Tuple

from ..constants import PROJECT_ROOT
from ..inputs.sprites import (
    AnimationSpec,
    Palette,
    parse_animations,
    parse_facing,
    parse_palette,
    parse_rect,
)
from ..inputs.tuning import read_yaml

ENTITIES_FILE = PROJECT_ROOT / "res" / "entities.yaml"

KEYS = {
    "id", "name", "behaviour", "image", "frame", "flip", "facing", "palette",
    "unique", "description", "animations", "settings",
}


@dataclass(frozen=True)
class EntityType:
    """One entry of ``res/entities.yaml`` (its header explains every key)."""

    id: str
    name: str
    image: str
    # The Python behaviour (src/entities/spawner.py, ENTITY_CLASSES).
    behaviour: str = ""
    # Picture of the editor palette; the first frame of the first animation
    # when it is not given.
    frame: Optional[Tuple[int, int, int, int]] = None
    flip: bool = False
    facing: int = -1
    palette: Palette = ()
    unique: bool = False
    description: str = ""
    animations: Mapping[str, AnimationSpec] = field(default_factory=dict)
    # Constants of the behaviour class (camelCase keys: speed, wakeUpTime...).
    settings: Mapping[str, Any] = field(default_factory=dict)
    # Where the settings come from, named in the error messages; a map gives
    # its own settings to a single entity (src/entities/spawner.py, tuned()).
    source: str = ""

    @property
    def where(self) -> str:
        """Name of the file the settings come from, for the error messages."""
        return self.source or f"entities.yaml: {self.id}"

    @property
    def editor_frame(self) -> Tuple[int, int, int, int]:
        """Picture of the editor palette: ``frame``, else the first frame of the first animation."""
        if self.frame is not None:
            return self.frame
        return next(iter(self.animations.values())).frames[0]


def parse_entity_type(entry: Any) -> EntityType:
    """Checks one entry of ``entities.yaml``; raises ValueError with its id."""
    if not isinstance(entry, Mapping) or not isinstance(entry.get("id"), str):
        raise ValueError(f"an entity needs an id: {entry!r}")
    kind = entry["id"]
    where = f"entity {kind!r}"
    unknown = set(entry) - KEYS
    if unknown:
        raise ValueError(f"{where}: unknown key(s) {', '.join(sorted(unknown))}")
    if not isinstance(entry.get("image"), str):
        raise ValueError(f"{where} needs the image id of its sheet")
    animations = parse_animations(entry.get("animations"), kind)
    frame = entry.get("frame")
    if frame is None and not animations:
        raise ValueError(f"{where} needs a frame or animations")
    settings = entry.get("settings") or {}
    if not isinstance(settings, Mapping):
        raise ValueError(f"{where}: settings must be a mapping")
    return EntityType(
        id=kind,
        name=str(entry.get("name", kind)),
        image=entry["image"],
        behaviour=str(entry.get("behaviour", kind)),
        frame=parse_rect(frame, f"{where}: frame") if frame is not None else None,
        flip=bool(entry.get("flip", False)),
        facing=parse_facing(entry.get("facing"), where),
        palette=parse_palette(entry.get("palette"), f"{where}: palette"),
        unique=bool(entry.get("unique", False)),
        description=str(entry.get("description", "")),
        animations=animations,
        settings=dict(settings),
    )


def load_entity_types(path: Path = ENTITIES_FILE) -> Dict[str, EntityType]:
    """Reads every entity type of the file, by id."""
    try:
        data = read_yaml(path)
        types: Dict[str, EntityType] = {}
        for entry in data.get("entities") or []:
            kind = parse_entity_type(entry)
            if kind.id in types:
                raise ValueError(f"two entities are called {kind.id!r}")
            types[kind.id] = kind
    except ValueError as error:
        raise ValueError(f"{Path(path).name}: {error}") from None
    return types


_types: Optional[Dict[str, EntityType]] = None


def entity_types() -> Dict[str, EntityType]:
    """The types of ``res/entities.yaml``, read once."""
    global _types
    if _types is None:
        _types = load_entity_types()
    return _types
