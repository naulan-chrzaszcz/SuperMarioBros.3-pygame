from dataclasses import dataclass


@dataclass(frozen=True)
class Tile:
    """A sheet tile placed in a map cell. ``rotation`` is in degrees."""

    x: int
    y: int
    x_frames: int = 1
    y_frames: int = 1
    rotation: int = 0

    @property
    def frames(self) -> int:
        return max(self.x_frames, self.y_frames)
