"""Settings of a single entity placed on the map.

Every entity of a type shares the settings of ``res/entities.yaml``; this model
gives one placed entity its own values (a faster goomba, a koopa that wakes up
later...) without touching the others. The editor knows nothing about the game
classes: the settings offered are the ones the type declares, and the values of
a text setting are the ones used anywhere in ``entities.yaml``.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from ..outputs.entity import Placement, Value
from ..outputs.map import Cell
from .entities import EntityType, text_choices
from .map_editor_model import MapEditorModel

# Smallest change of a number, and the part of the value one step changes.
MIN_INT_STEP = 1
MIN_FLOAT_STEP = 0.1
STEP_RATIO = 0.1


def value_label(value: Value) -> str:
    """The value as the panel shows it (``on``/``off`` for a switch)."""
    if isinstance(value, bool):
        return "on" if value else "off"
    if isinstance(value, float):
        return f"{value:g}"
    return str(value)


def next_value(value: Value, default: Value, step: int, choices: Tuple[str, ...]) -> Value:
    """``value`` changed by one step: a switch toggles, a number grows or
    shrinks and a text takes the next value used in ``entities.yaml``."""
    if isinstance(default, bool):
        return not value
    if isinstance(default, int):
        return max(value + step * max(abs(default) // 10, MIN_INT_STEP), 0)
    if isinstance(default, float):
        change = max(abs(default) * STEP_RATIO, MIN_FLOAT_STEP)
        return round(max(value + step * change, 0.0), 3)
    if not choices:
        return value
    index = choices.index(value) if value in choices else 0
    return choices[(index + step) % len(choices)]


class EntityPanel:
    """The entity being tuned, its settings and the changes the user can make.

    The panel is closed when no cell is being edited. Every change goes through
    the map model, so tuning an entity can be undone like any other edit.
    """

    def __init__(self, model: MapEditorModel, types: Tuple[EntityType, ...]) -> None:
        self.model = model
        self.types = types
        self.cell: Optional[Cell] = None
        self.index = 0

    @property
    def visible(self) -> bool:
        return self.placement is not None

    @property
    def placement(self) -> Optional[Placement]:
        """The entity being tuned; None when the panel is closed (or when the
        entity was removed, undone or pasted over)."""
        return None if self.cell is None else self.model.entities.get(self.cell)

    @property
    def kind(self) -> Optional[EntityType]:
        placement = self.placement
        if placement is None:
            return None
        return next((kind for kind in self.types if kind.id == placement.kind), None)

    @property
    def title(self) -> str:
        kind, placement = self.kind, self.placement
        if placement is None or self.cell is None:
            return ""
        name = kind.name if kind is not None else f"{placement.kind} (unknown)"
        return f"{name} at {self.cell[0]},{self.cell[1]}"

    @property
    def keys(self) -> Tuple[str, ...]:
        """Settings that can be changed on this entity, in declaration order."""
        kind = self.kind
        return () if kind is None else kind.tunable

    def open(self, cell: Cell) -> bool:
        """Tunes the entity of ``cell``; False when the cell holds none."""
        if self.model.entities.get(cell) is None:
            return False
        self.cell = cell
        self.index = 0
        return True

    def close(self) -> None:
        self.cell = None
        self.index = 0

    def select(self, index: int) -> None:
        keys = self.keys
        if keys:
            self.index = index % len(keys)

    def rows(self) -> List[Tuple[str, str]]:
        """``(setting, value)`` lines; a tuned value ends with a star."""
        placement = self.placement
        if placement is None:
            return []
        rows = []
        for key in self.keys:
            tuned = key in placement.settings
            rows.append((key, value_label(self.value(key)) + (" *" if tuned else "")))
        return rows

    def value(self, key: str) -> Value:
        """The value this entity uses: its own, else the one of its type."""
        placement, kind = self.placement, self.kind
        if placement is not None and key in placement.settings:
            return placement.settings[key]
        return None if kind is None else kind.settings.get(key)

    @property
    def selected_key(self) -> Optional[str]:
        keys = self.keys
        return keys[self.index] if keys and self.index < len(keys) else None

    @property
    def selected_label(self) -> str:
        key = self.selected_key
        return "" if key is None else value_label(self.value(key))

    def change(self, step: int) -> bool:
        """Changes the selected setting by one step (the step is a direction)."""
        key, kind = self.selected_key, self.kind
        if key is None or kind is None or self.cell is None:
            return False
        default = kind.settings.get(key)
        value = next_value(self.value(key), default, step, text_choices(self.types, key))
        if value == default:
            return self.reset()
        return self.model.set_entity_setting(self.cell, key, value)

    def reset(self) -> bool:
        """Gives the setting of the type back to the selected setting."""
        key = self.selected_key
        if key is None or self.cell is None:
            return False
        return self.model.set_entity_setting(self.cell, key, None)

    def reset_all(self) -> bool:
        """Makes the entity behave like every other entity of its type."""
        placement = self.placement
        if placement is None or self.cell is None or not placement.settings:
            return False
        changed = False
        with self.model.edit():
            for key in list(placement.settings):
                changed |= self.model.set_entity_setting(self.cell, key, None)
        return changed
