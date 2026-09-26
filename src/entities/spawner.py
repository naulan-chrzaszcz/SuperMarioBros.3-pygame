"""Turns the entities placed with the map editor into living entities.

``res/entities.yaml`` names the behaviour of each type: several types can
share a behaviour with other pictures and settings (the green and the red
koopa are both ``koopa``). ``generic`` is the behaviour of an entity that
needs no Python at all: its settings choose what it does.
"""

from __future__ import annotations

from typing import Callable, Dict, Iterable, List, Mapping, Optional, Tuple, Type

from ..animation import SpriteBank
from ..inputs.map import EntitySpawn
from ..inputs.tuning import check
from .catalog import EntityType, entity_types
from .entity import Entity
from .koopa import Koopa

# Behaviour of Mario's starting point: a marker, not an entity.
START = "start"

ENTITY_CLASSES: Dict[str, Type[Entity]] = {
    "generic": Entity,
    "koopa": Koopa,
}


def validate_entity_types(types: Mapping[str, EntityType]) -> None:
    """Checks the behaviours, settings and animations of ``entities.yaml``
    when the game starts, rather than when a level spawns the entity."""
    for kind in types.values():
        where = f"entities.yaml: {kind.id}"
        if kind.behaviour == START:
            continue
        cls = ENTITY_CLASSES.get(kind.behaviour)
        if cls is None:
            known = ", ".join([START, *ENTITY_CLASSES])
            raise ValueError(f"{where}: unknown behaviour {kind.behaviour!r} (known: {known})")
        values = check(cls, kind.settings, where)
        cls.check_effects(where, values)
        missing = [name for name in cls.required_animations(values) if name not in kind.animations]
        if missing:
            raise ValueError(f"{where} needs the animation(s) {', '.join(missing)}")


def spawn_entities(
    spawns: Iterable[EntitySpawn],
    sprites: SpriteBank,
    is_solid: Callable[[int, int], bool],
    types: Optional[Mapping[str, EntityType]] = None,
) -> Tuple[List[Entity], Optional[EntitySpawn]]:
    """The entities of a map and its start marker (None when it has none).

    Entities that can hide, placed on a solid cell, are hidden in its block.
    """
    types = entity_types() if types is None else types
    entities: List[Entity] = []
    start = None
    for spawn in spawns:
        kind = types.get(spawn.type)
        if kind is None:
            raise ValueError(f"Unknown entity type: {spawn.type!r}")
        if kind.behaviour == START:
            start = spawn
            continue
        cls = ENTITY_CLASSES.get(kind.behaviour)
        if cls is None:
            raise ValueError(f"Entity {kind.id!r} has an unknown behaviour: {kind.behaviour!r}")
        entity = cls(kind, sprites, spawn.column, spawn.row)
        if entity.CAN_HIDE and is_solid(spawn.column, spawn.row):
            entity.hide()
        entities.append(entity)
    return entities, start


def known_types() -> List[str]:
    return list(entity_types())
