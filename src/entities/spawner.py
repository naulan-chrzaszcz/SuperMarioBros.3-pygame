"""Turns the entities placed with the map editor into living entities.

``res/entities.yaml`` names the behaviour of each type: several types can
share a behaviour with other pictures and settings (the green and the red
koopa are both ``koopa``). ``generic`` is the behaviour of an entity that
needs no Python at all: its settings choose what it does.
"""

from __future__ import annotations

from dataclasses import replace
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
        where = kind.where
        if kind.behaviour == START:
            continue
        cls = ENTITY_CLASSES.get(kind.behaviour)
        if cls is None:
            known = ", ".join([START, *ENTITY_CLASSES])
            raise ValueError(f"{where}: unknown behaviour {kind.behaviour!r} (known: {known})")
        validate_settings(kind, cls)


def validate_settings(kind: EntityType, cls: Type[Entity]) -> None:
    """Check the constants, effects and animations of one tuned entity type."""
    values = check(cls, kind.settings, kind.where)
    cls.check_effects(kind.where, values)
    missing = [name for name in cls.required_animations(values) if name not in kind.animations]
    if missing:
        raise ValueError(f"{kind.where} needs the animation(s) {', '.join(missing)}")


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
        entity = cls(tuned(kind, spawn), sprites, spawn.column, spawn.row)
        if entity.CAN_HIDE and is_solid(spawn.column, spawn.row):
            entity.hide()
        entities.append(entity)
    return entities, start


def known_types() -> List[str]:
    return list(entity_types())


def validate_spawns(spawns: Iterable[EntitySpawn]) -> None:
    """Check map overrides before offering a level as playable."""
    types = entity_types()
    for spawn in spawns:
        kind = types.get(spawn.type)
        if kind is None:
            raise ValueError(f"unknown entity type: {spawn.type!r}")
        if kind.behaviour == START:
            if spawn.settings:
                raise ValueError(f"start marker at {spawn.column},{spawn.row} cannot have settings")
            continue
        if not spawn.settings:
            continue
        cls = ENTITY_CLASSES.get(kind.behaviour)
        if cls is None:
            raise ValueError(f"entity {kind.id!r} has an unknown behaviour: {kind.behaviour!r}")
        validate_settings(tuned(kind, spawn), cls)


def tuned(kind: EntityType, spawn: EntitySpawn) -> EntityType:
    """The type of ``spawn``, with the settings the map gives to this entity
    only; the type is returned as it is when the map gives none."""
    if not spawn.settings:
        return kind
    return replace(
        kind,
        settings={**kind.settings, **spawn.settings},
        source=f"map: {kind.id} at {spawn.column},{spawn.row}",
    )
