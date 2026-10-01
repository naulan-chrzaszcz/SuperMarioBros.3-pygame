"""Resolve named tileset animation frames, regardless of their sheet positions."""

from __future__ import annotations

import re
from typing import Dict, List, Mapping, Tuple

Cell = Tuple[int, int]
Animations = Dict[Cell, Tuple[Cell, ...]]
FRAME_NAME = re.compile(r"^(.*)_frame_(\d+)$")


def tile_animations(entries: List[dict], size: Cell, source: str) -> Animations:
    """Build animations from frame names or explicit ordered name lists.

    A legacy axis/count definition is still accepted for existing tilesets.
    """
    names: Dict[str, Cell] = {}
    coordinates: Dict[Cell, str] = {}
    for tile in entries:
        cell = tile["coordinate"]["x"], tile["coordinate"]["y"]
        name = tile["name"]
        if name in names:
            raise ValueError(f"{source}: duplicate tile name {name!r}")
        if cell in coordinates:
            raise ValueError(f"{source}: tiles {name!r} and {coordinates[cell]!r} share a coordinate")
        if not (0 <= cell[0] < size[0] and 0 <= cell[1] < size[1]):
            raise ValueError(f"{source}: tile {name!r} is outside the sheet image")
        names[name] = cell
        coordinates[cell] = name

    groups: Dict[str, Dict[int, str]] = {}
    for name in names:
        match = FRAME_NAME.fullmatch(name)
        if match:
            group, index = match.group(1), int(match.group(2))
            if index in groups.setdefault(group, {}):
                raise ValueError(f"{source}: duplicate frame index in {group!r}")
            groups[group][index] = name

    animations: Animations = {}
    occupied: Dict[Cell, str] = {}
    for tile in entries:
        name = tile["name"]
        animation = tile.get("animation")
        match = FRAME_NAME.fullmatch(name)
        if animation is None and (match is None or int(match.group(2)) != 0):
            continue
        where = f"{source}: tile {name!r} animation"
        if animation is None:
            members = groups[match.group(1)]
            if len(members) < 2:
                continue
            if set(members) != set(range(len(members))):
                raise ValueError(f"{where} has missing frame indices")
            frames = [names[members[index]] for index in range(len(members))]
        elif isinstance(animation, Mapping) and set(animation) == {"frames"}:
            listed = animation["frames"]
            if not isinstance(listed, list) or len(listed) < 2 or any(
                not isinstance(member, str) for member in listed
            ):
                raise ValueError(f"{where} needs at least two declared frame names")
            for member in listed:
                if member not in names:
                    raise ValueError(f"{where} references unknown tile {member!r}")
            frames = [names[member] for member in listed]
        elif isinstance(animation, Mapping) and set(animation) == {"axis", "frames"}:
            axis, count = animation["axis"], animation["frames"]
            if axis not in ("x", "y") or type(count) is not int or count < 2:
                raise ValueError(f"{where} needs an axis (x/y) and at least 2 frames")
            x, y = names[name]
            frames = [(x + index, y) if axis == "x" else (x, y + index)
                      for index in range(count)]
        else:
            raise ValueError(f"{where} needs a list of frame names")
        if frames[0] != names[name] or len(set(frames)) != len(frames):
            raise ValueError(f"{where} must start at its own tile and contain no duplicate frames")
        for cell in frames:
            if not (0 <= cell[0] < size[0] and 0 <= cell[1] < size[1]):
                raise ValueError(f"{where} goes outside the sheet image")
            if cell in occupied:
                raise ValueError(f"{where} overlaps animation of {occupied[cell]!r}")
            occupied[cell] = name
        animations[frames[0]] = tuple(frames)
    return animations
