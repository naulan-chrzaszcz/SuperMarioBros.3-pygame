"""Animations cut once from the sheets, as described in ``res/sprites.yaml``."""

from __future__ import annotations

from typing import Dict, List, Mapping, Optional, Tuple

from pygame import PixelArray, Rect, Surface, transform

from .inputs.sprites import AnimationSpec, Palette, SpriteSpec, load_sprite_specs


def recolored(surface: Surface, palette: Palette) -> Surface:
    """A copy of ``surface`` with the colors of ``palette`` swapped."""
    if not palette:
        return surface
    surface = surface.copy()
    pixels = PixelArray(surface)
    for source, target in palette:
        pixels.replace(source, target)
    pixels.close()
    return surface


class Animation:
    """Frames facing both ways; :meth:`image` picks the one of a moment."""

    def __init__(self, frames: List[Surface], period: float = 0.0, mirror: bool = False, facing: int = -1):
        if not frames:
            raise ValueError("An animation needs at least one frame")
        self.period = period
        self.mirror = mirror
        self.facing = facing
        flipped = [transform.flip(frame, True, False) for frame in frames]
        self._frames = {facing: frames, -facing: flipped}

    def __len__(self) -> int:
        return len(self._frames[self.facing])

    @property
    def duration(self) -> float:
        return self.period * len(self)

    def step(self, time: float) -> int:
        """Number of frames shown since ``time`` 0."""
        return int(time / self.period) if self.period > 0 else 0

    def image(self, time: float = 0.0, facing: Optional[int] = None) -> Surface:
        """The frame at ``time`` seconds, looking to ``facing`` (-1 left, 1
        right; None: as drawn in the sheet)."""
        step = self.step(time)
        count = len(self)
        facing = self.facing if facing is None else facing
        # A mirrored animation plays its frames, then plays them again flipped.
        if self.mirror and (step // count) % 2:
            facing = -facing
        return self._frames[facing][step % count]

    def frame(self, index: int, facing: Optional[int] = None) -> Surface:
        frames = self._frames[self.facing if facing is None else facing]
        return frames[index % len(frames)]


class Animator:
    """Plays an :class:`Animation` on a pygame sprite (sets its ``image``)."""

    def __init__(self, sprite, animation: Animation):
        self.sprite = sprite
        self.animation = animation
        self.time = 0.0

    def reset(self) -> None:
        self.time = 0.0
        self.sprite.image = self.animation.image(0.0)

    def update(self, dt: float) -> None:
        self.time += dt
        self.sprite.image = self.animation.image(self.time)


class SpriteBank:
    """The animations of ``res/sprites.yaml``, cut on first use.

    ``ressources`` gives the images by id (see ``ressources.yaml``).
    """

    def __init__(self, ressources, specs: Optional[Mapping[str, SpriteSpec]] = None):
        self.ressources = ressources
        self.specs = dict(load_sprite_specs() if specs is None else specs)
        self._cache: Dict[Tuple, Dict[str, Animation]] = {}

    def spec(self, sprite: str) -> SpriteSpec:
        try:
            return self.specs[sprite]
        except KeyError:
            raise KeyError(f"Sprite {sprite!r} is not declared in sprites.yaml") from None

    def animations(self, sprite: str) -> Dict[str, Animation]:
        spec = self.spec(sprite)
        return self.build(spec.image, spec.animations, spec.facing, spec.palette, sprite)

    def animation(self, sprite: str, name: str) -> Animation:
        animations = self.animations(sprite)
        try:
            return animations[name]
        except KeyError:
            raise KeyError(f"Sprite {sprite!r} has no animation {name!r} in sprites.yaml") from None

    def image(self, sprite: str, name: str) -> Surface:
        """The first frame of an animation, as drawn in the sheet."""
        return self.animation(sprite, name).frame(0)

    def position(self, sprite: str, name: str) -> Tuple[int, int]:
        try:
            return self.spec(sprite).positions[name]
        except KeyError:
            raise KeyError(f"Sprite {sprite!r} has no position {name!r} in sprites.yaml") from None

    def build(
        self,
        image: str,
        specs: Mapping[str, AnimationSpec],
        facing: int = -1,
        palette: Palette = (),
        owner: str = "",
    ) -> Dict[str, Animation]:
        """Cuts ``specs`` in the image ``image`` (also used by the entities)."""
        key = (image, tuple(sorted(specs.items())), facing, palette)
        if key not in self._cache:
            sheet = self.ressources.image(image)
            bounds = sheet.get_rect()
            animations = {}
            for name, spec in specs.items():
                frames = []
                for rect in spec.frames:
                    if not bounds.contains(Rect(rect)):
                        raise ValueError(
                            f"{owner or image}/{name}: the frame {list(rect)} is outside "
                            f"the image {image!r} ({bounds.width}x{bounds.height})"
                        )
                    frames.append(recolored(sheet.subsurface(rect), palette))
                animations[name] = Animation(frames, spec.period, spec.mirror, facing)
            self._cache[key] = animations
        return self._cache[key]
