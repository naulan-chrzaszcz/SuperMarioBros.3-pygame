"""Tile strip animation, used by the animated tiles of the maps."""

from __future__ import annotations

from typing import List

from pygame import Surface, transform


class SpriteAnimation:
    """Cycles the image of a sprite through the frames of a sheet strip.

    ``image`` holds ``frames`` images side by side (``"x"``) or stacked
    (``"y"``). Frames are cut and rotated once, not on every update.
    """

    def __init__(
        self,
        sprite,
        image: Surface,
        frames: int,
        speed: float,
        subsurface_direction: str = "x",
        rotation: int = 0,
    ):
        if frames < 1:
            raise ValueError("An animation needs at least one frame")
        if subsurface_direction not in ("x", "y"):
            raise ValueError(f"Unknown animation direction: {subsurface_direction!r}")
        self.sprite = sprite
        self.speed = speed
        self.timer = 0.0
        self.frames = self.cut(image, frames, subsurface_direction, rotation)

    @classmethod
    def from_frames(cls, sprite, frames: List[Surface], speed: float) -> "SpriteAnimation":
        """Animate arbitrary sheet cells without requiring a contiguous strip."""
        if not frames:
            raise ValueError("An animation needs at least one frame")
        animation = cls.__new__(cls)
        animation.sprite = sprite
        animation.speed = speed
        animation.timer = 0.0
        animation.frames = frames
        return animation

    @staticmethod
    def cut(image: Surface, frames: int, direction: str, rotation: int = 0) -> List[Surface]:
        width, height = image.get_size()
        if direction == "x":
            width //= frames
        else:
            height //= frames
        cut = []
        for frame in range(frames):
            offset = (frame * width, 0) if direction == "x" else (0, frame * height)
            cut.append(transform.rotate(image.subsurface(offset, (width, height)), rotation))
        return cut

    @property
    def frame(self) -> int:
        return int(self.timer) % len(self.frames)

    def reset(self) -> None:
        self.timer = 0.0
        self.sprite.image = self.frames[0]

    def update(self, dt: float) -> None:
        self.timer = (self.timer + self.speed * dt) % len(self.frames)
        self.sprite.image = self.frames[self.frame]
