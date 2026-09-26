"""The entities of ``res/entities.yaml`` that can be placed on a map.

The game reads the same file (``src/entities/catalog.py``) and gives each type
its behaviour.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Mapping, Optional, Tuple

import yaml

from ..constants import DEFAULT_COLOR_KEY, ENTITIES_FILE, PROJECT_ROOT, RESSOURCES_FILE
from ..outputs.entity import Placement, Value

Color = Tuple[int, int, int]

__all__ = ["Color", "EntityType", "Placement", "Value", "load_entity_types", "text_choices"]


@dataclass(frozen=True)
class EntityType:
    """Entity metadata from YAML used by palettes, rendering and placement rules."""

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
    # The ``settings`` block of the type: the values every entity of this type
    # uses, and the ones a placed entity can override (see Placement).
    settings: Mapping[str, Value] = field(default_factory=dict)

    @property
    def tunable(self) -> Tuple[str, ...]:
        """Settings the editor can change on a single placed entity: the ones
        the type declares, except the lists (a palette is not a value to tune)."""
        return tuple(
            key for key, value in self.settings.items()
            if isinstance(value, (bool, int, float, str))
        )


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
            frame=editor_frame(entry),
            color_key=(key["r"], key["g"], key["b"]) if key else None,
            flip=bool(entry.get("flip", False)),
            palette=tuple((tuple(a), tuple(b)) for a, b in entry.get("palette", [])),
            unique=bool(entry.get("unique", False)),
            description=str(entry.get("description", "")),
            settings=dict(entry.get("settings") or {}),
        ))
    return tuple(types)


def text_choices(types: Tuple[EntityType, ...], key: str) -> Tuple[str, ...]:
    """Values used for the text setting ``key`` anywhere in ``entities.yaml``.

    The editor knows nothing about the game classes: the file itself lists the
    behaviours to choose from (``onStomp: squash`` on a goomba lets any other
    entity be squashed too).
    """
    values: list = []
    for kind in types:
        value = kind.settings.get(key)
        if isinstance(value, str) and not isinstance(value, bool) and value not in values:
            values.append(value)
    return tuple(values)


def editor_frame(entry: dict) -> Tuple[int, int, int, int]:
    """The ``frame`` of the entry, else the first frame of its first
    animation (see the header of res/entities.yaml)."""
    if entry.get("frame"):
        return tuple(entry["frame"])
    for animation in (entry.get("animations") or {}).values():
        frames = animation.get("frames") if isinstance(animation, dict) else animation
        if frames and isinstance(frames[0], (list, tuple)):
            frames = frames[0]
        if frames and len(frames) == 4:
            return tuple(frames)
    return (0, 0, 16, 16)


def _ressource_images(path: Path) -> Dict[str, dict]:
    try:
        with Path(path).open(encoding="utf-8") as file:
            entries = (yaml.safe_load(file) or {}).get("images", [])
    except (OSError, yaml.YAMLError):
        return {}
    return {entry["id"]: entry for entry in entries if "id" in entry}
