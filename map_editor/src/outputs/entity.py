"""One entity placed on a map, as the JSON map format stores it.

Like :mod:`map_editor.src.outputs.tile` for tiles, this module holds a map
value and nothing else: what the entity looks like and what it can do is the
business of ``res/entities.yaml`` (see ``map_editor/src/models/entities.py``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional

# A setting value: what YAML (and JSON) can hold for a game constant.
Value = Any


@dataclass(frozen=True)
class Placement:
    """An entity placed on a map: its type and its own settings.

    ``settings`` holds only what differs from the type: an empty mapping means
    the entity behaves exactly like every other entity of its type, while
    ``{"speed": 80.0}`` makes this goomba (and only this one) faster.
    """

    kind: str
    settings: Mapping[str, Value] = field(default_factory=dict)

    @property
    def tuned(self) -> bool:
        """True when this entity does not behave like the others of its type."""
        return bool(self.settings)

    def with_setting(self, key: str, value: Optional[Value]) -> "Placement":
        """The same entity with one setting changed; ``None`` gives the setting
        of the type back."""
        settings = dict(self.settings)
        if value is None:
            settings.pop(key, None)
        else:
            settings[key] = value
        return Placement(self.kind, settings)
