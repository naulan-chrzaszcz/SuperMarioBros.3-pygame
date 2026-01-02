from dataclasses import dataclass


@dataclass
class TileModel:
    x: int
    y: int
    x_frames: int
    y_frames: int
    rotation: int
