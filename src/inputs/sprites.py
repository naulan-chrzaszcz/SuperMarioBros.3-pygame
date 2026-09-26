"""Named animations cut in the images of ``ressources.yaml``.

``res/sprites.yaml`` (and the ``animations`` of ``res/entities.yaml``) describe
the frames with their rectangles in the sheet, so that the code only asks for
``mario / big_walk`` and never holds pixel coordinates. An animation is
written as:

- a single rectangle ``[x, y, width, height]``;
- a list of rectangles, shown one after the other;
- a mapping ``{frames: ..., period: seconds per frame, mirror: true}``;
  ``mirror`` plays the frames, then plays them again flipped (the goomba
  walk is one frame and its mirror image).

This module only reads data; :mod:`src.animation` cuts the images.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Mapping, Tuple

from ..constants import SPRITES_FILE
from .tuning import read_yaml

Rect4 = Tuple[int, int, int, int]
Color = Tuple[int, int, int]
Palette = Tuple[Tuple[Color, Color], ...]
Point = Tuple[int, int]

FACINGS = {"left": -1, "right": 1}


@dataclass(frozen=True)
class AnimationSpec:
    frames: Tuple[Rect4, ...]
    period: float = 0.0
    mirror: bool = False


@dataclass(frozen=True)
class SpriteSpec:
    """A sheet (``image`` id of ressources.yaml) and its named animations."""

    image: str
    animations: Mapping[str, AnimationSpec]
    # Where the frames of the sheet look: the code flips them for the other side.
    facing: int = -1
    palette: Palette = ()
    # Named points, e.g. where the HUD draws each value.
    positions: Mapping[str, Point] = field(default_factory=dict)


def _integers(value: Any, count: int, where: str) -> Tuple[int, ...]:
    if (
        not isinstance(value, (list, tuple))
        or len(value) != count
        or not all(isinstance(item, int) and not isinstance(item, bool) for item in value)
    ):
        raise ValueError(f"{where} must be a list of {count} whole numbers")
    return tuple(value)


def parse_rect(value: Any, where: str) -> Rect4:
    rect = _integers(value, 4, where)
    if rect[0] < 0 or rect[1] < 0 or rect[2] <= 0 or rect[3] <= 0:
        raise ValueError(f"{where}: invalid rectangle {list(rect)}")
    return rect  # type: ignore[return-value]


def parse_color(value: Any, where: str) -> Color:
    color = _integers(value, 3, where)
    if not all(0 <= channel <= 255 for channel in color):
        raise ValueError(f"{where}: color channels go from 0 to 255")
    return color  # type: ignore[return-value]


def parse_palette(value: Any, where: str) -> Palette:
    """``[[from r, g, b], [to r, g, b]]`` color swaps."""
    if value is None:
        return ()
    if not isinstance(value, (list, tuple)):
        raise ValueError(f"{where} must be a list of [from color, to color] pairs")
    swaps = []
    for pair in value:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise ValueError(f"{where} must be a list of [from color, to color] pairs")
        swaps.append((parse_color(pair[0], where), parse_color(pair[1], where)))
    return tuple(swaps)


def parse_animation(value: Any, where: str) -> AnimationSpec:
    period, mirror = 0.0, False
    if isinstance(value, Mapping):
        unknown = set(value) - {"frames", "period", "mirror"}
        if unknown:
            raise ValueError(f"{where}: unknown key(s) {', '.join(sorted(unknown))}")
        period = value.get("period", 0.0)
        if isinstance(period, bool) or not isinstance(period, (int, float)) or period < 0:
            raise ValueError(f"{where}: period must be a positive number of seconds")
        mirror = value.get("mirror", False)
        if not isinstance(mirror, bool):
            raise ValueError(f"{where}: mirror must be true or false")
        value = value.get("frames")
    if isinstance(value, (list, tuple)) and value and isinstance(value[0], int):
        value = [value]
    if not isinstance(value, (list, tuple)) or not value:
        raise ValueError(f"{where} needs at least one frame [x, y, width, height]")
    frames = tuple(parse_rect(rect, where) for rect in value)
    return AnimationSpec(frames, float(period), mirror)


def parse_animations(value: Any, where: str) -> Dict[str, AnimationSpec]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError(f"{where}: animations must be a mapping of names to frames")
    return {str(name): parse_animation(frames, f"{where}/{name}") for name, frames in value.items()}


def parse_facing(value: Any, where: str) -> int:
    if value is None:
        return -1
    if value not in FACINGS:
        raise ValueError(f"{where}: facing must be left or right")
    return FACINGS[value]


def parse_sprite(name: str, value: Any) -> SpriteSpec:
    if not isinstance(value, Mapping):
        raise ValueError(f"sprite {name!r} must be a mapping")
    unknown = set(value) - {"image", "animations", "facing", "palette", "positions"}
    if unknown:
        raise ValueError(f"sprite {name!r}: unknown key(s) {', '.join(sorted(unknown))}")
    if not isinstance(value.get("image"), str):
        raise ValueError(f"sprite {name!r} needs the image id of its sheet")
    positions = value.get("positions") or {}
    if not isinstance(positions, Mapping):
        raise ValueError(f"sprite {name!r}: positions must be a mapping of names to [x, y]")
    return SpriteSpec(
        image=value["image"],
        animations=parse_animations(value.get("animations"), name),
        facing=parse_facing(value.get("facing"), name),
        palette=parse_palette(value.get("palette"), f"{name}/palette"),
        positions={
            str(key): _integers(point, 2, f"{name}/positions/{key}")  # type: ignore[misc]
            for key, point in positions.items()
        },
    )


def load_sprite_specs(path: Path = SPRITES_FILE) -> Dict[str, SpriteSpec]:
    try:
        data = read_yaml(path)
        return {str(name): parse_sprite(str(name), value) for name, value in data.items()}
    except ValueError as error:
        message = str(error)
        prefix = f"{Path(path).name}: "
        raise ValueError(message if message.startswith(prefix) else prefix + message) from None
