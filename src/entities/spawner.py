"""Turns the entities placed with the map editor into living entities."""

from __future__ import annotations

from typing import Callable, Dict, Iterable, List, Optional, Tuple, Type

from ..inputs.map import EntitySpawn
from .entity import Entity, Sprites
from .goomba import Goomba
from .koopa import Koopa
from .mushroom import Mushroom, OneUp

# Mario's starting point: a marker, not an entity.
START = "start"

ENTITY_CLASSES: Dict[str, Type[Entity]] = {
    cls.TYPE: cls for cls in (Goomba, Koopa, Mushroom, OneUp)
}


def spawn_entities(
    spawns: Iterable[EntitySpawn],
    sprites: Sprites,
    is_solid: Callable[[int, int], bool],
) -> Tuple[List[Entity], Optional[EntitySpawn]]:
    """The entities of a map and its start marker (None when it has none).

    Items placed on a solid cell are hidden in the block of that cell.
    """
    entities: List[Entity] = []
    start = None
    for spawn in spawns:
        if spawn.type == START:
            start = spawn
            continue
        cls = ENTITY_CLASSES.get(spawn.type)
        if cls is None:
            raise ValueError(f"Unknown entity type: {spawn.type!r}")
        entity = cls(sprites, spawn.column, spawn.row)
        if isinstance(entity, Mushroom) and is_solid(spawn.column, spawn.row):
            entity.hide()
        entities.append(entity)
    return entities, start


def known_types() -> List[str]:
    return [START, *ENTITY_CLASSES]
