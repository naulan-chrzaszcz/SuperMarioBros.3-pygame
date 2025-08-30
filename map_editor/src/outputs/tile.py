from dataclasses import dataclass


@dataclass
class Tile:
    x: int
    y: int
    x_frames: int
    y_frames: int
    rotation: int
