"""``res/rules.yaml``: the gameplay values (physics, scores, durations...).

Each section tunes the constants of one class; a missing file or setting keeps
the default written in the code.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Mapping

from ..constants import RULES_FILE
from .tuning import read_yaml

# Section of rules.yaml -> what it tunes (for the error messages).
SECTIONS = {
    "player": "Mario's movement (src/platformer.py, Body)",
    "level": "platform levels (src/scenes/platform_level_scene.py)",
    "worldMap": "world map (src/scenes/levels_scene.py)",
}


@dataclass(frozen=True)
class Rules:
    """Sections of ``res/rules.yaml``; ``tune(obj, rules.player)`` applies one."""

    sections: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)

    def section(self, name: str) -> Dict[str, Any]:
        return dict(self.sections.get(name) or {})

    @property
    def player(self) -> Dict[str, Any]:
        return self.section("player")

    @property
    def level(self) -> Dict[str, Any]:
        return self.section("level")

    @property
    def world_map(self) -> Dict[str, Any]:
        return self.section("worldMap")

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Rules":
        unknown = set(data) - set(SECTIONS)
        if unknown:
            raise ValueError(
                f"unknown section(s) {', '.join(sorted(unknown))} (known: {', '.join(SECTIONS)})"
            )
        for name, values in data.items():
            if values is not None and not isinstance(values, Mapping):
                raise ValueError(f"section {name!r} must be a mapping")
        return cls(dict(data))

    @classmethod
    def load(cls, path: Path = RULES_FILE) -> "Rules":
        """Reads the file; errors name it (``rules.yaml: ...``)."""
        try:
            return cls.from_dict(read_yaml(path))
        except ValueError as error:
            raise ValueError(f"{Path(path).name}: {error}") from None
